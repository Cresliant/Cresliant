from dearpygui import dearpygui as dpg
from PIL import Image


class ResizeModule:
    name = "Resize"
    tooltip = "Resize image"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output

    def new(self):
        input_image = dpg.get_item_user_data("Input").image
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
                    label="Resize",
                    width=150,
                    default_value=100,
                    max_value=200,
                    min_value=1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = dpg.get_value("resize_percentage_" + tag)
        width = dpg.get_value("width_size_" + tag)
        height = dpg.get_value("height_size_" + tag)
        if width != image.width or height != image.height:
            return image.resize((width, height))

        return image.resize((int(image.width * percent / 100), int(image.height * percent / 100)))
