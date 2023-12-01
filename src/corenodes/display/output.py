from dearpygui import dearpygui as dpg


class OutputModule:
    def __init__(self, texture) -> None:
        self.texture = texture

    name: str = "Output"
    tooltip: str = "Image result"

    def run(self, path):
        if dpg.does_item_exist("Node_Modified_image"):
            dpg.delete_item("Node_Modified_image")
        try:
            with dpg.node(
                parent="MainNodeEditor",
                tag="Node_Modified_image",
                label="Result image",
                pos=[10, 10],
            ):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_image_button(
                        self.texture, tag="default_image_button", width=400, height=400
                    )

            with dpg.popup("Node_Modified_image"):
                dpg.add_button(
                    label="Delete",
                    callback=lambda: dpg.delete_item("Node_Modified_image"),
                )
        except Exception as e:
            pass
