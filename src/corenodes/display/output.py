from dearpygui import dearpygui as dpg


class OutputModule:
    name = "Output"
    tooltip = "Image output"

    def __init__(self, texture) -> None:
        self.counter = 0
        self.texture = texture

    def new(self):
        if dpg.does_item_exist("Output"):
            dpg.delete_item("Output")

        with dpg.node(
            parent="MainNodeEditor",
            tag="Output",
            label="Output",
            pos=[500, 10],
            user_data=self,
        ):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_image(self.texture)
