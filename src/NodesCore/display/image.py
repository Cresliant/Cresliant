from dearpygui import dearpygui as dpg


class ImageModule:
    def __init__(self, texture) -> None:
        self.texture = texture
    name: str = "Image"
    tooltip: str = "Image module"



    def run(self, path):
        if dpg.does_item_exist("Node_Default_image"):
            dpg.delete_item("Node_Default_image")
        try:
            with dpg.node(parent="MainNodeEditor", tag="Node_Default_image", label="Default image", pos=[10, 10]):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_image_button(self.texture, tag="default_image_button", width=400, height=400)

            with dpg.popup("Node_Default_image"):
                dpg.add_button(label="Delete", callback=lambda: dpg.delete_item("Node_Default_image"))
        except Exception as e:
            pass
