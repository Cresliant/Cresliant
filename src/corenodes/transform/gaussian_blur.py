from dearpygui import dearpygui as dpg
from PIL import Image, ImageFilter

from src.utils import find_available_pos, theme


class GaussianBlurModule:
    name = "Blur"
    tooltip = "Blur image"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output
        self.settings = {}

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="GaussianBlur_" + str(self.counter),
            label="Gaussian Blur",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="blur_gaussian_percentage_" + str(self.counter),
                    width=150,
                    default_value=0,
                    max_value=500,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

            dpg.bind_item_theme("GaussianBlur_" + str(self.counter), theme.green)

        self.settings["GaussianBlur_" + str(self.counter)] = {"blur_gaussian_percentage_" + str(self.counter): 0}
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        return image.filter(
            ImageFilter.GaussianBlur(radius=self.settings[tag]["blur_gaussian_percentage_" + tag.split("_")[1]] / 65)
        )
