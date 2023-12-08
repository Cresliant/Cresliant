import json
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image

from src.corenodes.display import InputModule, OutputModule
from src.corenodes.transform import (
    BlurModule,
    BrightnessModule,
    ContrastModule,
    ResizeModule,
    RotateModule,
    SharpnessModule,
)
from src.utils.nodes import HistoryItem, Link, history_manager
from src.utils.paths import resource_path


class NodeEditor:
    _name = "Node Editor"
    _tag = "MainNodeEditor"

    debug = True

    modules = []
    _node_links = []

    _project = None

    path = []

    def __init__(self, pillow_image: Image.Image):
        self.modules = [
            InputModule(pillow_image, self.update_output),
            ResizeModule(self.update_output),
            RotateModule(self.update_output),
            BlurModule(self.update_output),
            BrightnessModule(self.update_output),
            ContrastModule(self.update_output),
            SharpnessModule(self.update_output),
            OutputModule("output_0"),
        ]

    def start(self):
        history_manager.update_path = self.update_path
        history_manager.update_output = self.update_output
        history_manager.links = self._node_links

        with dpg.node_editor(
            tag=self._tag,
            callback=self.link_callback,
            delink_callback=self.delink_callback,
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_TopRight,
        ):
            self.modules[0].new()
            self.modules[-1].new()

        for module in self.modules[1:-1]:
            with dpg.tooltip(parent=module.name):
                dpg.add_text(module.tooltip)
            with dpg.tooltip(parent=module.name + "_popup"):
                dpg.add_text(module.tooltip)

    def update_path(self):
        self.path.clear()
        for node in dpg.get_all_items():
            try:
                data_ = dpg.get_item_user_data(node)
            except SystemError:
                continue
            if data_ and data_.name == "Input":
                self.path.append(node)
                break

        while True:
            link = dpg.get_item_info(self.path[-1])["children"][1][-1]
            found = False
            for link_ in self._node_links:
                if link_.source == link:
                    try:
                        self.path.append(dpg.get_item_info(link_.target)["parent"])
                    except SystemError:
                        continue

                    found = True
                    break

            if not found:
                break

    def update_output(self, sender=None, app_data=None, history=True):
        if sender and app_data:
            try:
                node = dpg.get_item_info(dpg.get_item_info(sender)["parent"])["parent"]
                module = dpg.get_item_user_data(node)
            except SystemError:
                return

            alias = dpg.get_item_alias(node)
            if history or history is None:
                history_manager.append(
                    HistoryItem(
                        tag=alias,
                        action="update",
                        data={sender: (app_data, module.settings[alias][sender])},
                    )
                )
            module.settings[alias][sender] = app_data
        try:
            output = dpg.get_item_user_data(self.path[-1])
        except IndexError:
            dpg.delete_item("Output_attribute", children_only=True)
            return
        if output.name != "Output":
            dpg.delete_item("Output_attribute", children_only=True)
            return

        image = dpg.get_item_user_data("Input").image
        for node in self.path[1:-1]:
            tag = dpg.get_item_alias(node)
            node = dpg.get_item_user_data(node)
            image = node.run(image, tag)

        dpg.delete_item(output.image)
        try:
            dpg.remove_alias(output.image)
        except SystemError:
            pass

        counter = output.image.split("_")[-1]
        output.image = "output_" + str(int(counter) + 1)
        output.pillow_image = image
        with dpg.texture_registry():
            dpg.add_static_texture(
                image.width,
                image.height,
                np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0,
                tag=output.image,
            )
        dpg.delete_item("Output_attribute", children_only=True)
        dpg.add_image(output.image, parent="Output_attribute")

    def link_callback(self, sender, app_data):
        for link in self._node_links:
            if link.source == app_data[0]:
                try:
                    dpg.delete_item(link.id)
                except SystemError:
                    continue
                self._node_links.remove(link)

        link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        self._node_links.append(Link(source=app_data[0], target=app_data[1], id=int(link)))
        history_manager.append(
            HistoryItem(
                tag=str(link),
                action="link_create",
                data={
                    "source": app_data[0],
                    "target": app_data[1],
                    "id": link,
                },
            )
        )

        self.update_path()
        self.update_output()

    def delink_callback(self, _sender, app_data):
        dpg.delete_item(app_data)
        for link in self._node_links:
            if link.id == app_data:
                history_manager.append(
                    HistoryItem(
                        tag=str(app_data),
                        action="link_delete",
                        data={
                            "source": link.source,
                            "target": link.target,
                            "id": link.id,
                        },
                    )
                )
                self._node_links.remove(link)
                break

        self.update_path()
        self.update_output()

    def delete_nodes(self, _sender, _app_data):
        for node in dpg.get_selected_nodes(self._tag):
            data = dpg.get_item_user_data(node)
            if data.protected:
                continue

            node_links = dpg.get_item_info(node)["children"][1]
            history_manager.append(
                HistoryItem(
                    tag=dpg.get_item_alias(node),
                    action="delete",
                    data={
                        "user_data": data,
                        "settings": data.settings[dpg.get_item_alias(node)],
                        "pos": dpg.get_item_pos(node),
                        "links": node_links,
                    },
                )
            )

            dpg.delete_item(node)
            for link in self._node_links:
                if link.source in node_links or link.target in node_links:
                    self._node_links.remove(link)

        self.update_path()
        self.update_output()

    def delete_links(self, _sender, _app_data):
        for link in dpg.get_selected_links(self._tag):
            dpg.delete_item(link)
            for link_ in self._node_links:
                if link_.id == link:
                    history_manager.append(
                        HistoryItem(
                            tag=str(link),
                            action="link_delete",
                            data={
                                "source": link_.source,
                                "target": link_.target,
                                "id": link_.id,
                            },
                        )
                    )
                    self._node_links.remove(link_)
                    break

        self.update_path()
        self.update_output()

    def duplicate_nodes(self, _sender=None, _app_data=None):
        for node in dpg.get_selected_nodes(self._tag):
            data_ = dpg.get_item_user_data(node)
            if not data_.protected:
                data_.new()

    def reset(self, _sender=None, _app_data=None):
        for node in dpg.get_all_items():
            try:
                data_ = dpg.get_item_user_data(node)
            except SystemError:
                continue
            if data_ and not data_.protected:
                dpg.delete_item(node)

        self._node_links.clear()
        history_manager.clear()
        self._project = None

        self.modules[0].new()
        self.modules[-1].new()

        self.update_path()
        self.update_output()

    def save(self):
        data = {"nodes": {}, "links": [], "image": dpg.get_item_user_data("Input").image_path}
        for node in dpg.get_all_items():
            try:
                data_ = dpg.get_item_user_data(node)
            except SystemError:
                continue
            if data_:
                data["nodes"][dpg.get_item_alias(node)] = {
                    "pos": dpg.get_item_pos(node),
                    "settings": data_.settings if hasattr(data_, "settings") else {},
                }

        for link in self._node_links:
            data["links"].append(
                {
                    "source": str(dpg.get_item_user_data(dpg.get_item_info(link.source)["parent"])),
                    "target": str(dpg.get_item_user_data(dpg.get_item_info(link.target)["parent"])),
                }
            )

        if self._project:
            with open(self._project, "w") as file:
                file.write(json.dumps(data))
            return

        location = asksaveasfilename(
            filetypes=[("Cresliant", "*.cresliant")],
            defaultextension=".cresliant",
            initialfile="project.cresliant",
            initialdir=os.curdir,
        )
        with open(location, "w") as file:
            file.write(json.dumps(data))

        self._project = location

    def open(self):
        try:
            location = askopenfilename(
                filetypes=[("Cresliant", "*.cresliant")],
                initialdir=os.curdir,
            )
            data = json.load(open(location))
        except FileNotFoundError:
            return

        self.reset()

        nodes = []
        for node in data["nodes"]:
            module = None
            for module_ in self.modules:
                if module_.name.lower() in node.lower():
                    module = module_
                    break

            if not module:
                continue

            module.new()

            if "_" in node:
                tag = node.split("_", maxsplit=2)[0] + "_" + str(module.counter - 1)
            else:
                tag = node

            nodes.append(tag)
            dpg.set_item_pos(tag, data["nodes"][node]["pos"])

            for setting in data["nodes"][node]["settings"].get(node, {}):
                setting_tag = "_".join(setting.split("_")[0:-1]) + "_" + str(module.counter - 1)
                dpg.set_value(setting_tag, data["nodes"][node]["settings"][node][setting])
                module.settings[tag][setting_tag] = data["nodes"][node]["settings"][node][setting]

        try:
            image = Image.open(data["image"])
            self.modules[0].viewer.load(image)
            self.modules[0].image = image
            self.modules[0].image_path = data["image"]
        except FileNotFoundError:
            pass

        for link in data["links"]:
            source = None
            target = None
            for node in nodes:
                check = node.split("_", maxsplit=2)[0]
                if check in link["source"]:
                    source = dpg.get_item_info(node)["children"][1][-1]
                elif check in link["target"]:
                    target = dpg.get_item_info(node)["children"][1][0]

            if not source or not target:
                continue

            link = dpg.add_node_link(
                source,
                target,
                parent=self._tag,
            )
            self._node_links.append(Link(source=source, target=target, id=int(link)))

        self._project = location
        self.update_path()
        self.update_output()


node_editor = NodeEditor(Image.open(resource_path("icon.ico")))
