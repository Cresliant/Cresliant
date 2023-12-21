from __future__ import annotations

import contextlib
import threading
from typing import TypeVar

import dearpygui.dearpygui as dpg
from PIL.Image import Image

TextureTag = TypeVar("TextureTag", bound=int)

try:
    import numpy as np

    def _image_to_1d_array(image: Image) -> np.array:
        return np.array(image, dtype=np.float32).ravel() / 255

except ModuleNotFoundError:
    import logging

    logger = logging.getLogger("DearPyGui_ImageController")
    logger.warning("numpy not installed. In DPG assets will take longer to load (about 8 times slower).")

    def _image_to_1d_array(image: Image) -> list:
        img_1D_array = []
        image_data = image.getdata()
        if image_data.bands == 3:
            for pixel in image_data:
                img_1D_array.extend((pixel[0] / 255, pixel[1] / 255, pixel[2] / 255, 1))
        else:
            for pixel in image_data:
                img_1D_array.extend((pixel[0] / 255, pixel[1] / 255, pixel[2] / 255, pixel[3] / 255))
        del image_data
        return img_1D_array


texture_registry: int | str = 0
texture_plug: TextureTag = None


def set_texture_registry(texture_registry_tag: int | str):
    global texture_registry
    texture_registry = texture_registry_tag


def get_texture_plug() -> TextureTag:
    global texture_plug
    if texture_plug is None:
        texture_plug = dpg.add_static_texture(width=1, height=1, default_value=[0] * 4, parent=texture_registry)
    return texture_plug


def image_to_dpg_texture(image: Image) -> TextureTag:
    rgba_image = image.convert("RGBA")
    img_1d_array = _image_to_1d_array(rgba_image)
    dpg_texture_tag = dpg.add_static_texture(
        width=rgba_image.width, height=rgba_image.height, default_value=img_1d_array, parent=texture_registry
    )

    rgba_image.close()
    del img_1d_array, rgba_image
    return dpg_texture_tag


class HandlerDeleter:
    """Prevents the DPG from shutting down suddenly.
    Removes the Handler after a period of time.
    """

    deletion_queue = []

    __thread: bool = False

    @classmethod
    def add(cls, handler: int | str):
        """Adds a handler to the deletion queue
        :param handler: DPG handler
        """
        if not cls.__thread:
            cls.__thread = True
            threading.Thread(target=cls._worker, daemon=True).start()
        cls.deletion_queue.append(handler)

    @classmethod
    def _worker(cls):
        while True:
            for _ in range(2):
                dpg.split_frame()

            if len(cls.deletion_queue) == 0:
                break

            deletion_queue = cls.deletion_queue.copy()
            cls.deletion_queue.clear()

            for _ in range(70):
                dpg.split_frame()

            for handler in deletion_queue:
                with contextlib.suppress(Exception):
                    dpg.delete_item(handler)
            del deletion_queue
        cls.__thread = False
