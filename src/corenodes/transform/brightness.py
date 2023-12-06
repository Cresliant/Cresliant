from dearpygui import dearpygui as dpg
from PIL import Image, ImageEnhance

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class BrightnessModule(NodeParent):
    name = "Brightness"
    tooltip = "Adjust brightness"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="brightness_" + str(self.counter),
            label="Brightness",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="brightness_percentage_" + str(self.counter),
                    width=150,
                    max_value=100,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        dpg.bind_item_theme("brightness_" + str(self.counter), theme.yellow)
        self.settings["brightness_" + str(self.counter)] = {"brightness_percentage_" + str(self.counter): 0}
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = self.settings["brightness_" + tag]["brightness_percentage_" + tag]
        return ImageEnhance.Brightness(image).enhance(percent / 25)
