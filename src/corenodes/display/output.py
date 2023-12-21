from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import theme


class OutputModule:
    name = "Output"
    tooltip = "Image output"

    def __init__(self, image):
        self.counter = 0
        self.image = image
        self.pillow_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        self.protected = True
        self.is_plugin = False

    def new(self):
        if dpg.does_item_exist("Output"):
            dpg.delete_item("Output")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Output",
            label="Output",
            pos=[800, 100],
            user_data=self,
        ), dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag="Output_attribute"):
            dpg.add_image(self.image)

        dpg.bind_item_theme("Output", theme.red)
