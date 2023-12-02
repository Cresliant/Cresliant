from tkinter.filedialog import askopenfilename

import numpy as np
from dearpygui import dearpygui as dpg
from PIL import Image


def pick_image(path, width, height):
    try:
        image = Image.open(path)
    except:
        return

    image = image.convert("RGBA")
    image = image.resize((width, height))
    image = np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0

    dpg.set_value("input_image", image)


class InputModule:
    name = "Input"
    tooltip = "Image input"

    def __init__(self, texture: str, width: int, height: int):
        self.texture = texture
        self.width = width
        self.height = height

    def run(self):
        if dpg.does_item_exist("Input"):
            dpg.delete_item("Input")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Input",
            label="Input",
            pos=[10, 10],
            user_data=self,
        ):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, user_data="input"):
                dpg.add_image(self.texture)
                dpg.add_button(
                    label="Choose Image",
                    width=120,
                    height=50,
                    callback=lambda: dpg.set_value(
                        "Input",
                        pick_image(
                            askopenfilename(
                                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")],
                            ),
                            self.width,
                            self.height,
                        ),
                    ),
                )
