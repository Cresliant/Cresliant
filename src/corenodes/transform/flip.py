from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class FlipModule(NodeParent):
    name = "Flip"
    tooltip = "Flip image"

    def __init__(self):
        super().__init__()

    def new(self, history=True):
        with dpg.node(
            parent="MainNodeEditor",
            tag="flip_" + str(self.counter),
            label="Flip",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_combo(
                    tag="flip_mode_" + str(self.counter),
                    label="Direction",
                    items=["Horizontal", "Vertical", "Diagonal"],
                    default_value="Horizontal",
                    width=150,
                    callback=self.update_output,
                )

        tag = "flip_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.yellow)
        self.settings[tag] = {"flip_mode_" + str(self.counter): "Horizontal"}
        self.end(tag, history)

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        mode_tag = "flip_mode_" + tag.split("_")[-1]
        if self.settings[tag][mode_tag] == "Horizontal":
            return image.transpose(Image.FLIP_LEFT_RIGHT)
        if self.settings[tag][mode_tag] == "Vertical":
            return image.transpose(Image.FLIP_TOP_BOTTOM)

        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        return image.transpose(Image.FLIP_TOP_BOTTOM)
