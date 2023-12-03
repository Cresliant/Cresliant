from dearpygui import dearpygui as dpg
from PIL import Image


class ResizeModule:
    name = "Resize"
    tooltip = "Resize image"

    def __init__(self, width: int, height: int, update_output: callable):
        self.counter = 0
        self.width = width
        self.height = height
        self.update_output = update_output

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="resize_" + str(self.counter),
            label="Resize image",
            pos=[500, 20],
            user_data=self,
        ):
            with dpg.node_attribute():
                dpg.add_input_int(
                    tag="width_size_" + str(self.counter),
                    label="width",
                    width=100,
                    default_value=self.width,
                    callback=self.update_output,
                )
                dpg.add_input_int(
                    tag="height_size_" + str(self.counter),
                    label="height",
                    width=100,
                    default_value=self.height,
                    callback=self.update_output,
                )

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="resize_percentage_" + str(self.counter),
                    label="Resize",
                    width=150,
                    default_value=100,
                    max_value=200,
                    min_value=0,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = dpg.get_value("resize_percentage_" + tag)
        return image.resize(
            (
                int(dpg.get_value("width_size_" + tag) * percent / 100),
                int(dpg.get_value("height_size_" + tag) * percent / 100),
            )
        )
