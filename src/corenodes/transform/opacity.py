from dearpygui import dearpygui as dpg
from PIL import Image

from src.utils import find_available_pos, theme
from src.utils.nodes import NodeParent


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
                    default_value=100,
                    max_value=100,
                    min_value=-1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = "opacity_" + str(self.counter)
        dpg.bind_item_theme(tag, theme.yellow)
        self.settings[tag] = {"opacity_percentage_" + str(self.counter): 255}
        if history:
            self.update_history(tag)
        self.counter += 1

    def run(self, image: Image.Image, tag: str) -> Image.Image:
        image.putalpha(self.settings[tag]["opacity_percentage_" + tag.split("_")[-1]] * 255 // 100)
        image = image.convert("RGBA")
        datas = image.getdata()
        newData = []
        for item in datas:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        image.putdata(newData)
        return image
