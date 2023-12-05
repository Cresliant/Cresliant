from dearpygui import dearpygui as dpg
from PIL import Image, ImageEnhance

from src.utils import find_available_pos, theme


class ContrastModule:
    name = "Contrast"
    tooltip = "Adjust contrast"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output
        self.settings = {}

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="contrast_" + str(self.counter),
            label="Contrast",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="contrast_percentage_" + str(self.counter),
                    width=150,
                    max_value=100,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

            dpg.bind_item_theme("contrast_" + str(self.counter), theme.yellow)

        self.settings["contrast_" + str(self.counter)] = {"contrast_percentage_" + str(self.counter): 0}
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = self.settings["contrast_" + tag]["contrast_percentage_" + tag]
        return ImageEnhance.Contrast(image).enhance(percent / 25)
