from __future__ import annotations

import contextlib
import queue
import threading
import time
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import dearpygui.dearpygui as dpg
from PIL import Image as img
from PIL.Image import LANCZOS, Image

from . import tools

if TYPE_CHECKING:
    from _typeshed import SupportsRead

    from .tools import TextureTag
    from .viewers import ImageViewerCreator

ImageControllerTag = TypeVar("ImageControllerTag", bound=str)
ImageLoadStatus = TypeVar("ImageLoadStatus", bound=bool)
ControllerType = TypeVar("ControllerType", bound="Controller")
SubscriptionTag = TypeVar("SubscriptionTag", bound=int)
ImageControllerType = TypeVar("ImageControllerType", bound="ImageController")

T_ImageViewerCreator = TypeVar("T_ImageViewerCreator", bound="ImageViewerCreator")


class ImageController:
    image: Image | None = None
    tag_in_controller: ImageControllerTag
    subscribers: dict[SubscriptionTag, type[T_ImageViewerCreator]]
    # Tag an already loaded DPG texture with this picture.
    # If loaded is False, the texture plug will be used.
    texture_tag: TextureTag

    last_time_visible: time.time = 0

    loading: bool = False
    loaded: bool = False

    def __init__(self, image: Image, tag_in_controller: ImageControllerTag, controller: ControllerType):
        self.image = image
        self.tag_in_controller = tag_in_controller
        self.controller = controller
        self.subscribers = {}
        self.texture_tag = tools.get_texture_plug()

    def subscribe(self, image_viewer: type[ImageViewerCreator]) -> SubscriptionTag:
        subscription_tag = dpg.generate_uuid()
        self.subscribers[subscription_tag] = image_viewer
        return subscription_tag

    def unsubscribe(self, subscription_tag: SubscriptionTag):
        if subscription_tag in self.subscribers:
            del self.subscribers[subscription_tag]
        if len(self.subscribers) == 0:
            del self.controller[self.tag_in_controller]
            self.image = None
            self.controller = None
            self.unload()

    def is_unloading_time(self) -> bool:
        if self.image:
            return (time.time() - self.last_time_visible) > self.controller.max_inactive_time
        return True

    def update_last_time_visible(self):
        """Updates the last time the picture was visible.
        Also, if an image has been unloaded,
        it will be loaded back in, using the loader worker
        """
        self.last_time_visible = time.time()
        if self.loaded or self.image is None:
            return
        if not self.loading:
            with contextlib.suppress(queue.Full):
                self.controller.loading_queue.put_nowait(self)
                self.loading = True

    def now_loading(self):
        for image_viewer in self.subscribers.values():
            try:
                image_viewer.now_loading()
            except Exception:
                traceback.print_exc()

    def load(self, texture_tag: TextureTag):
        self.texture_tag = texture_tag
        self.loaded = True
        self.loading = False
        if len(self.subscribers) == 0:
            self.unload()
            return

        try:
            for image_viewer in self.subscribers.values():
                try:
                    image_viewer.show(self.texture_tag)
                except Exception:
                    traceback.print_exc()
        except RuntimeError:
            return

        if self.image:
            self.controller.unload_queue.append(self)

    def unload(self):
        old_texture_tag = self.texture_tag
        self.texture_tag = tools.get_texture_plug()
        self.loaded = False
        self.loading = False
        for image_viewer in self.subscribers.values():
            try:
                image_viewer.hide()
            except Exception:
                traceback.print_exc()

        if old_texture_tag != tools.get_texture_plug():
            try:
                dpg.delete_item(old_texture_tag)
            except Exception:
                traceback.print_exc()


class Worker:
    STOP = False
    THREAD_RUNNING = False

    def start_thread(self):
        self.STOP = False
        if self.THREAD_RUNNING:
            return
        self.THREAD_RUNNING = True

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while not self.STOP:
            self.loop()

    def loop(self):
        ...

    def stop(self):
        self.STOP = True


class ImageUnloaderWorker(Worker):
    def __init__(self, unload_queue: list[ImageController], controller: ControllerType):
        self.queue = unload_queue
        self.controller = controller
        self.start_thread()

    def loop(self):
        for image_controller in self.queue:
            if image_controller.is_unloading_time():
                image_controller.unload()
                self.queue.remove(image_controller)
        time.sleep(self.controller.unloading_check_sleep_time)


class ImageLoaderWorker(Worker):
    def __init__(self, loading_queue: queue.LifoQueue[ImageController]):
        self.queue = loading_queue
        self.start_thread()

    @staticmethod
    def load(image_controller: ImageController):
        if not image_controller.loading:
            return
        if image_controller.is_unloading_time() or image_controller.loaded:
            image_controller.loading = False
            return

        image_controller.now_loading()
        try:
            image_controller.load(tools.image_to_dpg_texture(image_controller.image))
        except Exception:  # TODO: ValueError: Operation on closed image
            traceback.print_exc()

        image_controller.loading = False

    def loop(self):
        image_controller = self.queue.get()
        if self.STOP:
            self.queue.put(image_controller)
            return
        self.load(image_controller)
        self.queue.task_done()


class Controller(dict[ImageControllerTag, ImageController]):
    """Stores all hash pictures and associates it with ImageController.
    Also with the help of workers loads assets into the DPG
    """

    loading_queue: queue.LifoQueue[ImageController]
    loading_workers: list[ImageLoaderWorker]

    unload_queue: list[ImageController]
    unloading_worker: ImageUnloaderWorker

    max_inactive_time: int | float
    unloading_check_sleep_time: int | float
    _disable_work_in_threads: bool = False
    _last_time_unload_check: time.time = time.time()

    @property
    def disable_work_in_threads(self):
        return self._disable_work_in_threads

    @disable_work_in_threads.setter
    def disable_work_in_threads(self, value: bool):
        self._disable_work_in_threads = value
        for worker in self.loading_workers:
            if value:
                worker.stop()
            else:
                worker.start_thread()
        if value:
            self.unloading_worker.stop()
        else:
            self.unloading_worker.start_thread()

    def __init__(
        self,
        max_inactive_time: int = 10,
        unloading_check_sleep_time: int | float = 2.5,
        number_image_loader_workers: int = 2,
        queue_max_size: int = None,
        disable_work_in_threads: bool = False,
    ):
        """:param max_inactive_time: Time in seconds after which the picture will be unloaded from the DPG/RAM
        :param unloading_check_sleep_time: In this number of seconds the last visibility of the image will be checked
        :param number_image_loader_workers: Number of simultaneous loading of assets
        :param queue_max_size: If not set, it will be equal to number_image_loader_workers * 2
        :param disable_work_in_threads: Disables multi-threaded image un/loading
        """
        super().__init__()

        self.max_inactive_time = max_inactive_time
        self.unloading_check_sleep_time = unloading_check_sleep_time
        if queue_max_size is None:
            queue_max_size = number_image_loader_workers * 2

        self.loading_queue = queue.LifoQueue(maxsize=queue_max_size)
        self.loading_workers = [ImageLoaderWorker(self.loading_queue) for _ in range(number_image_loader_workers)]
        self.unload_queue = []
        self.unloading_worker = ImageUnloaderWorker(self.unload_queue, self)
        self.disable_work_in_threads = disable_work_in_threads

    def add(
        self, image: str | bytes | Path | SupportsRead[bytes] | Image
    ) -> tuple[ImageControllerTag, ImageController]:
        """:param image: Pillow Image or the path to the image, or any other object that Pillow can open
        :return:
        """
        if not isinstance(image, Image):
            image = img.open(image)
        image: Image

        hash_image = image.resize((12, 12), LANCZOS).convert("L")
        pixels = list(hash_image.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if pixel < avg else "0" for pixel in pixels)
        image_tag = int(bits, 2).__format__("016x").upper()

        # Checking if an image has already been added
        if image_info := self.get(image_tag):
            return image_tag, image_info

        image_info = self[image_tag] = ImageController(image=image, tag_in_controller=image_tag, controller=self)
        return image_tag, image_info

    def load_images(self, max_count: int = None):
        """Only works if `.disable_load_in_threads` == False.
        Loads assets to the DPG that are in the queue to be displayed.

        :param max_count: (None - inf) Maximum number of assets that can be loaded
        """
        if not self.disable_work_in_threads:
            return

        while self.loading_queue.not_empty:
            if max_count is not None:
                max_count -= 1
                if max_count < 0:
                    return

            try:
                image_controller = self.loading_queue.get(block=False)
            except queue.Empty:
                return

            ImageLoaderWorker.load(image_controller)

    def unload_images(self, max_count: int = None):
        """Only works if `.disable_load_in_threads` == False.
        Unloads loaded assets (textures) from the DPG that are in the remove queue.

        :param max_count: (None - inf) Maximum number of assets that can be uploaded
        """
        if not self.disable_work_in_threads:
            return
        if time.time() - self._last_time_unload_check < self.unloading_check_sleep_time:
            return
        self._last_time_unload_check = time.time()

        for image_controller in self.unload_queue:
            if image_controller.is_unloading_time():
                if max_count is not None:
                    max_count -= 1
                    if max_count < 0:
                        return
                image_controller.unload()
                self.unload_queue.remove(image_controller)


default_controller = Controller()
