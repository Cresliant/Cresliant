from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class CropModule(NodeParent):
    name = "Crop"
    tooltip = "Crop image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        input_image = dpg.get_item_user_data("Input").image

        with dpg.node(
            parent="MainNodeEditor",
            tag="crop_" + str(self.counter),
            label="Crop",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_int(
                    tag="left_" + str(self.counter),
                    label="Left",
                    width=100,
                    default_value=0,
                    min_value=0,
                    max_value=input_image.width - 1,
                    callback=self.update_output,
                )
                dpg.add_input_int(
                    tag="top_" + str(self.counter),
                    label="Top",
                    width=100,
                    default_value=0,
                    min_value=0,
                    max_value=input_image.height - 1,
                    callback=self.update_output,
                )
                dpg.add_input_int(
                    tag="right_" + str(self.counter),
                    label="Right",
                    width=100,
                    default_value=input_image.width,
                    min_value=1,
                    max_value=input_image.width,
                    callback=self.update_output,
                )
                dpg.add_input_int(
                    tag="bottom_" + str(self.counter),
                    label="Bottom",
                    width=100,
                    default_value=input_image.height,
                    min_value=1,
                    max_value=input_image.height,
                    callback=self.update_output,
                )

        tag = "crop_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.blue)
        self.settings[tag] = {
            "left_" + str(self.counter): 0,
            "top_" + str(self.counter): 0,
            "right_" + str(self.counter): input_image.width,
            "bottom_" + str(self.counter): input_image.height,
        }
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        left = self.settings["crop_" + tag]["left_" + tag]
        top = self.settings["crop_" + tag]["top_" + tag]
        right = self.settings["crop_" + tag]["right_" + tag]
        bottom = self.settings["crop_" + tag]["bottom_" + tag]
        return image.crop((left, top, right, bottom))
