from dearpygui import dearpygui as dpg
from PIL import Image, ImageEnhance

from src.utils import find_available_pos


class SharpnessModule:
    name = "Sharpness"
    tooltip = "Adjust sharpness"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output
        self.settings = {}

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="sharpness_" + str(self.counter),
            label="Sharpness",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="sharpness_percentage_" + str(self.counter),
                    width=150,
                    max_value=100,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        self.settings["sharpness_" + str(self.counter)] = {"sharpness_percentage_" + str(self.counter): 0}
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = self.settings["sharpness_" + tag]["sharpness_percentage_" + tag]
        return ImageEnhance.Sharpness(image).enhance(percent / 25)
