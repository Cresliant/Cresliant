from dearpygui import dearpygui as dpg
from PIL import Image, ImageFilter

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class BlurModule(NodeParent):
    name = "Blur"
    tooltip = "Blur image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        with dpg.node(
            parent="MainNodeEditor",
            tag="blur_" + str(self.counter),
            label="Blur",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_combo(
                    tag="blur_mode_" + str(self.counter),
                    label="Mode",
                    items=["Gaussian", "Box"],
                    default_value="Gaussian",
                    width=150,
                    callback=self.update_output,
                )
                dpg.add_slider_int(
                    tag="blur_percentage_" + str(self.counter),
                    width=150,
                    default_value=1,
                    max_value=500,
                    min_value=1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = "blur_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.green)
        self.settings[tag] = {"blur_mode_" + str(self.counter): "Gaussian", "blur_percentage_" + str(self.counter): 1}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        if self.settings[tag]["blur_mode_" + tag.split("_")[-1]] == "Box":
            return image.filter(
                ImageFilter.BoxBlur(radius=self.settings[tag]["blur_percentage_" + tag.split("_")[-1]] / 50)
            )

        return image.filter(
            ImageFilter.GaussianBlur(radius=self.settings[tag]["blur_percentage_" + tag.split("_")[-1]] / 65)
        )
