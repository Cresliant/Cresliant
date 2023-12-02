from dearpygui import dearpygui as dpg


class ResizeModule:
    def __init__(self, width, height):
        self.counter = 0
        self.width = width
        self.height = height

    name = "Resize"
    tooltip = "Resize tool to modify image size"

    def run(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="resize_" + str(self.counter),
            label="Resize image",
            pos=[500, 20],
            user_data=self,
        ):
            with dpg.node_attribute():
                dpg.add_input_int(
                    tag="width_size_" + str(self.counter), label="width", width=100, default_value=self.width
                )
                dpg.add_input_int(
                    tag="height_size_" + str(self.counter), label="height", width=100, default_value=self.height
                )

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="resize_percentage_" + str(self.counter),
                    label="Resize in percentage",
                    width=150,
                    default_value=0,
                    max_value=100,
                    min_value=0,
                )

        self.counter += 1
