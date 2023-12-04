from dearpygui import dearpygui as dpg
from PIL import Image


class RotateModule:
    name = "Rotate"
    tooltip = "Rotate image"

    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output
        self.settings = {}

    def new(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="rotate_" + str(self.counter),
            label="Rotate",
            pos=[dpg.get_viewport_width() // 2 - 100, dpg.get_viewport_height() // 2 - 100],
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="rotate_degrees_" + str(self.counter),
                    width=150,
                    max_value=360,
                    clamped=True,
                    format="%0.0f°",
                    callback=self.update_output,
                )

        self.settings["rotate_" + str(self.counter)] = {"rotate_degrees_" + str(self.counter): 0}
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        return image.rotate(dpg.get_value("rotate_degrees_" + tag.split("_")[-1]))
