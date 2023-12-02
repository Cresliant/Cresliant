from dearpygui import dearpygui as dpg


class RotateModule:
    def __init__(self) -> None:
        self.counter = 0

    name = "Rotate"
    tooltip = "Rotate tool for rotating the image"

    def run(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="rotate_" + str(self.counter),
            label="Rotate image",
            pos=[500, 20],
        ):
            with dpg.node_attribute() as Resize_image:
                dpg.add_input_float(tag="rotate_degrees_" + str(self.counter), label="Rotate degrees", width=100)

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="rotate_percentage_" + str(self.counter),
                    label="Rotate in percentage",
                    width=150,
                    default_value=0,
                    max_value=360,
                    min_value=0,
                )

        self.counter += 1
