from tkinter.filedialog import askopenfilename

from dearpygui import dearpygui as dpg
from PIL import Image

import ImageController as dpg_img


class InputModule:
    name = "Input"
    tooltip = "Image input"

    def __init__(self, image: Image.Image, update_output: callable):
        self.counter = 0
        self.image = image
        self.viewer = None
        self.update_output = update_output

    def pick_image(self, path):
        try:
            image = Image.open(path)
        except:
            return

        image = image.convert("RGBA")
        image.thumbnail((450, 450), Image.LANCZOS)
        self.image = image
        self.viewer.load(image)
        self.update_output()

    def new(self):
        if dpg.does_item_exist("Input"):
            dpg.delete_item("Input")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Input",
            label="Input",
            pos=[10, 100],
            user_data=self,
        ):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                self.viewer = dpg_img.add_image(self.image)
                dpg.add_spacer(height=5)
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
