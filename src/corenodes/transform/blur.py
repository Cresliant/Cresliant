from dearpygui import dearpygui as dpg


class BlurModule:
    def __init__(self):
        self.counter = 0

    name = "Blur"
    tooltip = "Blur area / full image"

    def run(self):
        with dpg.node(
            parent="MainNodeEditor",
            tag="blur_" + str(self.counter),
            label="Blur image",
            pos=[600, 20],
        ):
            with dpg.node_attribute():
                dpg.add_input_int(tag="Blur_input" + str(self.counter), label="% Blur", width=100)

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="blur_percentage_" + str(self.counter),
                    label="% Blur in percentage",
                    width=150,
                    default_value=0,
                    max_value=100,
                    min_value=0,
                )

        self.counter += 1
