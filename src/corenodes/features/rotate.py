from dearpygui import dearpygui as dpg


class RotateModule:
    def __init__(self, img) -> None:
        self.img = img

    name: str = "Rotate"
    tooltip: str = "Rotate tool for rotating the image"

    def run(self):
        if dpg.does_item_exist("Node_Rotate_Image"):
            dpg.delete_item("Node_Rotate_Image")
        try:
            with dpg.node(
                parent="MainNodeEditor",
                tag="Node_Rotate_Image",
                label="Rotate image",
                pos=[500, 20],
            ):
                with dpg.node_attribute() as Resize_image:
                    dpg.add_input_float(
                        tag="Rotate_degrees", label="Rotate degrees", width=100
                    )

                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_slider_int(
                        tag="Rotate_Percentage",
                        label="Rotate in percentage",
                        width=150,
                        default_value=0,
                        max_value=360,
                        min_value=0,
                    )
        except Exception as e:
            pass
