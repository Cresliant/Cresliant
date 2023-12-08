from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent
from PIL import Image



class OpacityModule(NodeParent):
    name = "Opacity"
    tooltip = "Change image opacity"

    def __init__(self, update_output: callable):
        super().__init__(update_output)

    def new(self, history=True):
        with dpg.node(
            parent="MainNodeEditor",
            tag="opacity_" + str(self.counter),
            label="Opacity",
            pos=find_available_pos(),
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(
                    tag="opacity_percentage_" + str(self.counter),
                    width=150,
                    default_value=0,
                    max_value=255,
                    min_value=0,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = "opacity_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.green)
        self.settings[tag] = {"opacity_percentage_" + str(self.counter): 255}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        tag = tag.split("_")[-1]
        percent = self.settings["opacity_" + tag]["opacity_percentage_" + tag]

        datas = image.getdata()

        newData = []
        for item in datas:
            # Preserve the original RGB values and only change the alpha value
            newData.append((item[0], item[1], item[2], percent))

        image.putdata(newData)
        return image