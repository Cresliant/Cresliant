import os
import random

import dearpygui.dearpygui as dpg
import yaml
from PIL import ImageFilter
from PIL.Image import Image

from src.utils.nodes import NodeParent, theme


class Node(NodeParent):
    def __init__(self):
        # We load some universal variables from NodeParent that every node uses
        super().__init__()

        with open(os.path.dirname(__file__) + "/plugin.yaml") as file:
            self.info = yaml.safe_load(file)

        self.name = self.info["name"]
        self.tooltip = self.info["description"]

    def new(self, history=True):
        # This is where you create the node using dearpygui
        with dpg.node(
            parent="MainNodeEditor",
            tag=self.name + "_" + str(self.counter),
            label=self.name,
            user_data=self,
        ):
            dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_combo(
                    tag=self.name + "_mode_" + str(self.counter),
                    label="Mode",
                    items=["Party", "Disco"],
                    default_value="Party",
                    width=150,
                    callback=self.update_output,
                )
                dpg.add_slider_int(
                    tag=self.name + "_intensity_" + str(self.counter),
                    width=150,
                    default_value=1,
                    max_value=500,
                    min_value=1,
                    clamped=True,
                    format="%0.0f%%",
                    callback=self.update_output,
                )

        tag = self.name + "_" + str(self.counter)
        # You can provide an optional theme to the node
        dpg.bind_item_theme(tag, theme.yellow)
        # This is where you store the settings; they get automatically updated when the user changes them
        self.settings[tag] = {
            self.name + "_mode_" + str(self.counter): "Party",
            self.name + "_intensity_" + str(self.counter): 1,
        }
        # This is a boilerplate function that should be called at the end to make it work with the history
        self.end(tag, history)

    def run(self, image: Image, tag: str) -> Image:
        # This is the function that is called when the node is run
        # Anything can be done here, you take in a PIL image and return a PIL image with the changes
        intensity = self.settings[tag][self.name + "_intensity_" + tag.split("_")[-1]]
        if self.settings[tag][self.name + "_mode_" + tag.split("_")[-1]] == "Party":
            return image.point(lambda i: i + random.randint(0, intensity))

        filtered = image.filter(ImageFilter.GaussianBlur(radius=intensity / 65))
        return filtered.point(lambda i: i + random.randint(0, intensity))
