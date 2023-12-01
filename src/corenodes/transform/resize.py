from dearpygui import dearpygui as dpg


class ResizeModule:
    def __init__(self, img) -> None:
        self.img = img

    name: str = "Resize"
    tooltip: str = "Resize tool to modify image size"

    def run(self, width, height):
        # Check for nodes
        if dpg.does_item_exist("Node_Resize_Image"):
            dpg.delete_item("Node_Resize_Image")
        try:
            # Create node
            with dpg.node(
                parent="MainNodeEditor",
                tag="Node_Resize_Image",
                label="Resize image",
                pos=[500, 20],
            ):
                with dpg.node_attribute():
                    dpg.add_input_int(tag="x_size", label="x", width=100)
                    dpg.add_input_int(tag="y_size", label="y", width=100)
                    dpg.add_input_int(
                        tag="z_size",
                        label="z",
                        width=100,
                        default_value=self.img.size[0],
                    )
                    dpg.add_input_int(
                        tag="w_size",
                        label="w",
                        width=100,
                        default_value=self.img.size[1],
                    )

                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_slider_int(
                        tag="Resize_Percentage",
                        label="Resize in percentage",
                        width=150,
                        default_value=0,
                        max_value=100,
                        min_value=0,
                    )

            # Create node pop up
            with dpg.popup("Node_Resize_Image"):
                dpg.add_button(
                    label="Delete",
                    callback=lambda: dpg.delete_item("Node_Resize_Image"),
                )

        except Exception as e:
            pass
