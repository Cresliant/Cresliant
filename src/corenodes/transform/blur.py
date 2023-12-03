from dearpygui import dearpygui as dpg
from PIL import Image, ImageFilter


class BlurModule:
    name = "Blur"
    tooltip = "Blur image"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="blur_" + str(self.counter),
            label="Blur image",
            pos=[600, 20],
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="blur_percentage_" + str(self.counter),
                    label="Blur",
                    width=150,
                    default_value=0,
                    max_value=500,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = dpg.get_value("blur_percentage_" + tag)
        return image.filter(ImageFilter.GaussianBlur(radius=percent / 100))
