from dearpygui import dearpygui as dpg
from PIL import Image, ImageFilter

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class GaussianBlurModule(NodeParent):
    name = "Blur"
    tooltip = "Blur image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        with dpg.node(
            parent="MainNodeEditor",
            tag="gaussian_blur_" + str(self.counter),
            label="Gaussian Blur",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="blur_gaussian_percentage_" + str(self.counter),
                    width=150,
                    default_value=1,
                    max_value=500,
                    min_value=1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = "gaussian_blur_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.green)
        self.settings[tag] = {"blur_gaussian_percentage_" + str(self.counter): 1}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        return image.filter(
            ImageFilter.GaussianBlur(radius=self.settings[tag]["blur_gaussian_percentage_" + tag.split("_")[-1]] / 65)
        )
