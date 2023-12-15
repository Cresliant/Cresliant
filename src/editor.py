import importlib.util
import json
import os
import sys

import dearpygui.dearpygui as dpg
import yaml
from PIL import Image

from src.corenodes.display import InputModule, OutputModule
from src.corenodes.transform import (
    BlurModule,
    BrightnessModule,
    ContrastModule,
    CropModule,
    FlipModule,
    OpacityModule,
    ResizeModule,
    RotateModule,
    SharpnessModule,
)
from src.utils import fd, toaster
from src.utils.nodes import HistoryItem, Link, history_manager, update
from src.utils.paths import resource


class NodeEditor:
    _name = "Node Editor"
    _tag = "MainNodeEditor"

    debug = not hasattr(sys, "_MEIPASS")

    modules = []
    _data = None

    _project = None

    def __init__(self, pillow_image: Image.Image):
        self.modules = [
            InputModule(pillow_image),
            ResizeModule(),
            RotateModule(),
            BlurModule(),
            BrightnessModule(),
            ContrastModule(),
            SharpnessModule(),
            OpacityModule(),
            CropModule(),
            FlipModule(),
            OutputModule("output_0"),
        ]

        # Load all plugins from the plugins folder dynamically
        for plugin in os.listdir("src/plugins"):
            if not os.path.isdir("src/plugins/" + plugin):
                continue
            try:
                with open("src/plugins/" + plugin + "/plugin.yaml") as file:
                    info = yaml.safe_load(file)
            except FileNotFoundError:
                continue

            if info.get("enabled", True) is False:
                continue

            # install any requirements that the plugin depends on
            if info.get("requirements"):
                for requirement in info.get("requirements", []):
                    try:
                        version = f"=={requirement['version']}"
                    except KeyError:
                        version = ""
                    os.system(f"pip install {requirement['name']}{version}")

            file = info["runtime"]["main"]
            if not file.endswith(".py"):
                file += ".py"

            spec = importlib.util.spec_from_file_location("plugin", "src/plugins/" + plugin + "/" + file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if "Node" in dir(module):
                node = module.Node()
                node.is_plugin = True
                self.modules.insert(1, node)

    def start(self):
        history_manager.update_path = update.update_path
        history_manager.update_output = update.update_output
        history_manager.links = update.node_links

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
                if module.is_plugin:
                    continue
                dpg.add_text(module.tooltip)
            with dpg.tooltip(parent=module.name + "_popup"):
                if module.is_plugin:
                    continue
                dpg.add_text(module.tooltip)

    def link_callback(self, sender, app_data):
        for link in update.node_links:
            if link.source == app_data[0]:
                try:
                    dpg.delete_item(link.id)
                except SystemError:
                    continue
                update.node_links.remove(link)

        link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        update.node_links.append(Link(source=app_data[0], target=app_data[1], id=int(link)))
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

        update.update_path()
        update.update_output()

    def delink_callback(self, _sender, app_data):
        dpg.delete_item(app_data)
        for link in update.node_links:
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
                update.node_links.remove(link)
                break

        update.update_path()
        update.update_output()

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
            for link in update.node_links:
                if link.source in node_links or link.target in node_links:
                    update.node_links.remove(link)

        update.update_path()
        update.update_output()

    def delete_links(self, _sender, _app_data):
        for link in dpg.get_selected_links(self._tag):
            dpg.delete_item(link)
            for link_ in update.node_links:
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
                    update.node_links.remove(link_)
                    break

        update.update_path()
        update.update_output()

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
            try:
                if data_ and not data_.protected:
                    dpg.delete_item(node)
            except AttributeError:
                continue

        update.node_links.clear()
        history_manager.clear()
        self._project = None

        self.modules[0].new()
        self.modules[-1].new()

        update.update_path()
        update.update_output()

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

        for link in update.node_links:
            source = dpg.get_item_user_data(dpg.get_item_info(link.source)["parent"])
            target = dpg.get_item_user_data(dpg.get_item_info(link.target)["parent"])
            data["links"].append(
                {
                    "source": source.name,
                    "target": target.name,
                }
            )

        if self._project:
            with open(self._project, "w") as file:
                file.write(json.dumps(data))
            return toaster.show("Save Project", "Project saved successfully.")

        self._data = data
        fd.change(self.save_callback, True, ".cresliant")
        fd.show_file_dialog()

    def save_callback(self, info):
        try:
            filename = info[0]
            location = info[2]
        except IndexError:
            toaster.show("Save project", "Invalid location specified.")
            return

        if not filename.endswith(".cresliant"):
            filename += ".cresliant"

        location = os.path.join(location, filename)

        try:
            with open(location, "w") as file:
                file.write(json.dumps(self._data))
        except FileNotFoundError:
            toaster.show("Save Project", "Invalid location specified.")
            return

        self._project = location
        toaster.show("Save Project", "Project saved successfully.")

    def open(self):
        fd.change(self.open_callback, False, ".cresliant")
        fd.show_file_dialog()

    def open_callback(self, info):
        location = info[0]
        try:
            with open(location) as file:
                data = json.load(file)
        except FileNotFoundError:
            return toaster.show("Open Project", "Invalid location specified.")

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
            image = image.convert("RGBA")
            self.modules[0].image = image.copy()
            self.modules[0].image_path = data["image"]
            image.thumbnail((450, 450), Image.LANCZOS)
            self.modules[0].viewer.load(image)
        except FileNotFoundError:
            pass

        for link in data["links"]:
            source = None
            target = None
            for node in nodes:
                check = node.split("_", maxsplit=2)[0].lower()
                if check == link["source"].lower():
                    source = dpg.get_item_info(node)["children"][1][-1]
                elif check == link["target"].lower():
                    target = dpg.get_item_info(node)["children"][1][0]

            if not source or not target:
                continue

            link = dpg.add_node_link(
                source,
                target,
                parent=self._tag,
            )
            update.node_links.append(Link(source=source, target=target, id=int(link)))

        self._project = location
        update.update_path()
        update.update_output()
        toaster.show("Open Project", "Project opened successfully.")


node_editor = NodeEditor(Image.open(resource("icon.ico")))
