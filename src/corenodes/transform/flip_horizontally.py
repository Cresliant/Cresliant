from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class FlipHorizontallyModule(NodeParent):
    name = "Flip Horizontaly"
    tooltip = "Flip image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        input_image = dpg.get_item_user_data("Input").image

        with dpg.node(
            parent="MainNodeEditor",
            tag="flip_" + str(self.counter),
            label="Flip",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("This will flip the image")

        tag = "resize_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.blue)
        self.settings[tag] = {None}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        return image.transpose(Image.FLIP_LEFT_RIGHT)
