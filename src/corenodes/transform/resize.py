from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


class ResizeModule(NodeParent):
    name = "Resize"
    tooltip = "Resize image"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        input_image = dpg.get_item_user_data("Input").image

        with dpg.node(
            parent="MainNodeEditor",
            tag="resize_" + str(self.counter),
            label="Resize",
            pos=find_available_pos(),
            user_data=self,
        ):
            with dpg.node_attribute():
                dpg.add_input_int(
                    tag="width_size_" + str(self.counter),
                    label="width",
                    width=100,
                    default_value=input_image.width,
                    min_value=1,
                    min_clamped=True,
                    max_value=10000,
                    max_clamped=True,
                    callback=self.update_output,
                )
                dpg.add_input_int(
                    tag="height_size_" + str(self.counter),
                    label="height",
                    width=100,
                    min_value=1,
                    min_clamped=True,
                    max_value=10000,
                    max_clamped=True,
                    default_value=input_image.height,
                    callback=self.update_output,
                )

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="resize_percentage_" + str(self.counter),
                    width=150,
                    default_value=100,
                    max_value=500,
                    min_value=1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = "resize_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.blue)
        self.settings[tag] = {
            "width_size_" + str(self.counter): input_image.width,
            "height_size_" + str(self.counter): input_image.height,
            "resize_percentage_" + str(self.counter): 100,
        }
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = self.settings["resize_" + tag]["resize_percentage_" + tag]
        return image.resize(
            (
                self.settings["resize_" + tag]["width_size_" + tag] * percent // 100,
                self.settings["resize_" + tag]["height_size_" + tag] * percent // 100,
            ),
            Image.LANCZOS,
        )
