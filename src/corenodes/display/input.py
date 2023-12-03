from tkinter.filedialog import askopenfilename

import numpy as np
from dearpygui import dearpygui as dpg
from PIL import Image


class InputModule:
    name = "Input"
    tooltip = "Image input"

    def __init__(self, texture: str, pillow_image: Image.Image, update_output: callable):
        self.counter = 0
        self.texture = texture
        self.image = pillow_image
        self.update_output = update_output

    def pick_image(self, path):
        try:
            image = Image.open(path)
        except:
            return

        image = image.convert("RGBA")
        image.thumbnail((450, 450), Image.LANCZOS)
        width, height = image.size
        self.image = image

        image = np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0
        dpg.delete_item(self.texture)

        self.counter += 1
        self.texture = "input_image_" + str(self.counter)

        with dpg.texture_registry(show=False):
            dpg.add_static_texture(
                width=width,
                height=height,
                default_value=image,
                tag=self.texture,
            )

        self.new()
        self.update_output()

    def new(self):
        if dpg.does_item_exist("Input"):
            dpg.delete_item("Input")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Input",
            label="Input",
            pos=[10, 10],
            user_data=self,
        ):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_image(self.texture)
                dpg.add_button(
                    label="Choose Image",
                    width=120,
                    height=50,
                    callback=lambda: self.pick_image(
                        askopenfilename(
                            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")],
                        )
                    ),
                )

    def run(self, _image: Image.Image, _tag: str) -> Image.Image:
        return self.image
