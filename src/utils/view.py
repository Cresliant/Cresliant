import contextlib
import threading
from enum import Enum

import dearpygui.dearpygui as dpg


class AlignmentType(Enum):
    Horizontal = 0
    Vertical = 1
    Both = 2


def auto_align(item, alignment_type: AlignmentType, x_align: float = 0.5, y_align: float = 0.5):
    parent = "Cresliant"

    def _center_h(_s, _d, data):
        parentWidth = dpg.get_item_rect_size(parent)[0]
        width = dpg.get_item_rect_size(data[0])[0]
        newX = (parentWidth // 2 - width // 2) * data[1] * 2
        dpg.set_item_pos(data[0], [newX, dpg.get_item_pos(data[0])[1]])

    def _center_v(_s, _d, data):
        parentWidth = dpg.get_item_rect_size(parent)[1]
        height = dpg.get_item_rect_size(data[0])[1]
        newY = (parentWidth // 2 - height // 2) * data[1] * 2
        dpg.set_item_pos(data[0], [dpg.get_item_pos(data[0])[0], newY])

    with dpg.item_handler_registry():
        if alignment_type == AlignmentType.Horizontal:
            dpg.add_item_visible_handler(callback=_center_h, user_data=[item, x_align])
        elif alignment_type == AlignmentType.Vertical:
            dpg.add_item_visible_handler(callback=_center_v, user_data=[item, y_align])
        elif alignment_type == AlignmentType.Both:
            dpg.add_item_visible_handler(callback=_center_h, user_data=[item, x_align])
            dpg.add_item_visible_handler(callback=_center_v, user_data=[item, y_align])

    dpg.bind_item_handler_registry(item, dpg.last_container())


class Toaster:
    def __init__(self):
        self.parent = "MainNodeEditor"
        self.toasters = []

    def show(self, title, description, duration=5.0):
        toaster = "toaster_" + str(len(self.toasters))
        if dpg.does_item_exist(toaster):
            self.delete(toaster)
            with contextlib.suppress(SystemError):
                dpg.remove_alias(toaster)

        with dpg.window(
            tag=toaster,
            no_move=True,
            no_resize=True,
            no_collapse=True,
            label=title,
            pos=[
                dpg.get_item_rect_size(self.parent)[0] - 300,
                dpg.get_item_rect_size(self.parent)[1] - 50 - 110 * len(self.toasters),
            ],
            on_close=lambda s, d: self.delete(toaster),
            height=100,
            width=300,
        ):
            dpg.add_text(description, wrap=295)

        # with dpg.item_handler_registry():
        #     dpg.add_item_visible_handler(callback=lambda s, d, data: dpg.set_item_pos(toaster, [
        #         dpg.get_item_rect_size(self.parent)[0] - 300,
        #         dpg.get_item_rect_size(self.parent)[1] - 100 - 110 * self.toasters.index(toaster),
        #     ]), user_data=toaster)
        threading.Timer(duration, self.delete, [toaster]).start()
        self.toasters.append(toaster)

    def delete(self, toaster):
        if dpg.does_item_exist(toaster):
            dpg.delete_item(toaster)
        try:
            self.toasters.remove(toaster)
        except ValueError:
            return  # User must've dismissed the toaster manually

        for toaster in self.toasters:
            dpg.set_item_pos(
                toaster,
                [
                    dpg.get_item_rect_size(self.parent)[0] - 300,
                    dpg.get_item_rect_size(self.parent)[1] - 50 - 110 * self.toasters.index(toaster),
                ],
            )


toaster = Toaster()
