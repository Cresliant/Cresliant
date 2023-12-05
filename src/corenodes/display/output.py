from dearpygui import dearpygui as dpg

import ImageController as dpg_img
from src.utils import theme


class OutputModule:
    name = "Output"
    tooltip = "Image output"

    def __init__(self, image) -> None:
        self.counter = 0
        self.image = image
        self.viewer = None

    def new(self):
        if dpg.does_item_exist("Output"):
            dpg.delete_item("Output")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Output",
            label="Output",
            pos=[800, 100],
            user_data=self,
        ):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                self.viewer = dpg_img.add_image(self.image)

            dpg.bind_item_theme("Output", theme.red)
