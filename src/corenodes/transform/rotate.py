from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class RotateModule(NodeParent):
    name = "Rotate"
    tooltip = "Rotate image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        with dpg.node(
            parent="MainNodeEditor",
            tag="rotate_" + str(self.counter),
            label="Rotate",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="rotate_degrees_" + str(self.counter),
                    width=150,
                    min_value=1,
                    max_value=360,
                    default_value=360,
                    clamped=True,
                    format="%0.0f°",
                    callback=self.update_output,
                )

        tag = "rotate_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.green)
        self.settings[tag] = {"rotate_degrees_" + str(self.counter): 1}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        print(self.settings[tag]["rotate_degrees_" + tag.split("_")[1]])
        return image.rotate(self.settings[tag]["rotate_degrees_" + tag.split("_")[1]])
