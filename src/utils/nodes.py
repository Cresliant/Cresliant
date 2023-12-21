from contextlib import suppress

import dearpygui.dearpygui as dpg
import numpy as np
from PIL import Image
from pydantic import BaseModel


def find_available_pos():
    x, y = dpg.get_mouse_pos(local=False)
    return [max(0, x - 70), max(0, y - 70)]


class Link(BaseModel):
    source: int
    target: int
    id: int


class NodeParent:
    def __init__(self):
        self.counter = 0
        self.update_output = update.update_output
        self.settings = {}
        self.protected = False
        self.is_plugin = False

    def end(self, tag, history):
        # Do global boilerplate across all nodes
        if history:
            history_manager.append(
                HistoryItem(
                    tag=tag,
                    action="new",
                    data={
                        "settings": self.settings[tag],
                        "pos": dpg.get_item_pos(tag),
                        "user_data": dpg.get_item_user_data(tag),
                    },
                )
            )
        self.counter += 1


class Update:
    def __init__(self):
        self.path = []
        self.node_links = []

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
            for link_ in self.node_links:
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
        img_size = image.size
        for node in self.path[1:-1]:
            tag = dpg.get_item_alias(node)
            node = dpg.get_item_user_data(node)
            image = node.run(image, tag)

        dpg.delete_item(output.image)
        with suppress(SystemError):
            dpg.remove_alias(output.image)

        counter = output.image.split("_")[-1]
        output.image = "output_" + str(int(counter) + 1)
        output.pillow_image = image.copy()
        image.thumbnail((450, 450), Image.LANCZOS)
        with dpg.texture_registry():
            dpg.add_static_texture(
                image.width,
                image.height,
                np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0,
                tag=output.image,
            )
        dpg.delete_item("Output_attribute", children_only=True)
        dpg.add_image(output.image, parent="Output_attribute")
        if output.pillow_image.size != img_size:
            dpg.add_spacer(height=5, parent="Output_attribute")
            dpg.add_text(
                f"Image size: {output.pillow_image.width}x{output.pillow_image.height}", parent="Output_attribute"
            )


class HistoryItem(BaseModel):
    tag: str
    action: str
    data: dict


class HistoryManager:
    def __init__(self):
        self.history: list[HistoryItem] = []
        self.index = -1
        self.update_output = None
        self.update_path = None
        self.links = None

    def clear(self):
        self.history = []
        self.index = -1

    def append(self, item: HistoryItem):
        if self.index != len(self.history) - 1:
            self.history = self.history[: self.index + 1]

        self.history.append(item)
        self.index += 1

    def undo(self):
        if self.index >= 0:
            item = self.current
            try:
                match item.action:
                    case "new":
                        try:
                            self.history[self.index].data["pos"] = dpg.get_item_pos(item.tag)
                        except SystemError:
                            self.index = len(self.history) - 1
                            return
                        dpg.delete_item(item.tag)
                    case "update":
                        key, value = next(iter(item.data.items()))
                        try:
                            dpg.set_value(key, value[1])
                        except SystemError:
                            self.index = len(self.history) - 1
                            return
                        self.update_output(key, value[1], False)
                    case "delete":
                        data = item.data["user_data"]
                        data.new(history=False)
                        tag = "_".join(item.tag.split("_")[:-1]) + "_" + str(data.counter - 1)
                        dpg.set_item_pos(tag, item.data["pos"])
                        for key, value in item.data["settings"].items():
                            try:
                                dpg.set_value("_".join(key.split("_")[:-1]) + "_" + tag.split("_")[1], value)
                            except SystemError:
                                print(
                                    "Warning: Could not set value:",
                                    "_".join(key.split("_")[:-1]) + "_" + tag.split("_")[1],
                                    value,
                                )
                    case "link_delete":
                        tag = dpg.add_node_link(
                            item.data["source"],
                            item.data["target"],
                            parent="MainNodeEditor",
                        )
                        self.history[self.index].data["id"] = tag
                        self.links.append(Link(source=item.data["source"], target=item.data["target"], id=tag))
                        self.update_path()
                        self.update_output()
                    case "link_create":
                        dpg.delete_item(item.data["id"])
                        for link in self.links:
                            if link.source == item.data["source"] and link.target == item.data["target"]:
                                self.links.remove(link)
                        self.update_path()
                        self.update_output()
                    case _:
                        raise ValueError(f"Unknown action in undo: {item.action}")
            except SystemError:
                print("Warning: Could not undo action:", item.action)

            self.index -= 1

    def redo(self):
        if self.index < len(self.history) - 1:
            self.index += 1
            item = self.current
            try:
                match item.action:
                    case "new":
                        data = item.data["user_data"]
                        data.counter -= 1
                        try:
                            data.new(history=False)
                        except SystemError:
                            data.counter += 1
                            self.index = len(self.history) - 1
                            return

                        tag = "_".join(item.tag.split("_")[:-1]) + "_" + str(data.counter - 1)
                        dpg.set_item_pos(tag, item.data["pos"])
                        for key, value in item.data["settings"].items():
                            try:
                                dpg.set_value("_".join(key.split("_")[:-1]) + "_" + tag.split("_")[1], value)
                            except SystemError:
                                print(
                                    "Warning: Could not set value:",
                                    "_".join(key.split("_")[:-1]) + "_" + tag.split("_")[1],
                                    value,
                                )
                    case "update":
                        key, value = next(iter(item.data.items()))
                        try:
                            dpg.set_value(key, value[0])
                        except SystemError:
                            self.index = len(self.history) - 1
                            return
                        self.update_output(key, value[0], False)
                    case "delete":
                        try:
                            self.history[self.index].data["pos"] = dpg.get_item_pos(item.tag)
                        except SystemError:
                            self.index = len(self.history) - 1
                            return
                        dpg.delete_item(item.tag)
                    case "link_delete":
                        dpg.delete_item(item.data["id"])
                        for link in self.links:
                            if link.source == item.data["source"] and link.target == item.data["target"]:
                                self.links.remove(link)
                        self.update_path()
                        self.update_output()
                    case "link_create":
                        tag = dpg.add_node_link(
                            item.data["source"],
                            item.data["target"],
                            parent="MainNodeEditor",
                        )
                        self.history[self.index].data["id"] = tag
                        self.links.append(Link(source=item.data["source"], target=item.data["target"], id=tag))
                        self.update_path()
                        self.update_output()
                    case _:
                        raise ValueError(f"Unknown action in redo: {item.action}")
            except SystemError:
                print("Warning: Could not redo action:", item.action)

    @property
    def current(self):
        if self.history:
            return self.history[self.index]

        return None


class Theme:
    def __init__(self):
        self._cache = {}

    def _get_theme(self, color_name, color_value):
        cached = self._cache.get(color_name)
        if cached is not None:
            return cached

        with dpg.theme() as theme_id, dpg.theme_component(0):
            dpg.add_theme_color(dpg.mvNodeCol_TitleBar, color_value, category=dpg.mvThemeCat_Nodes)
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarHovered,
                (color_value[0] + 10, color_value[1] + 10, color_value[2] + 10),
                category=dpg.mvThemeCat_Nodes,
            )
            dpg.add_theme_color(
                dpg.mvNodeCol_TitleBarSelected,
                (color_value[0] + 25, color_value[1] + 25, color_value[2] + 25),
                category=dpg.mvThemeCat_Nodes,
            )

        self._cache[color_name] = theme_id
        return theme_id

    @property
    def red(self) -> int:
        return self._get_theme("red", (189, 62, 62))

    @property
    def green(self) -> int:
        return self._get_theme("green", (14, 128, 25))

    @property
    def blue(self) -> int:
        return self._get_theme("blue", (0, 63, 181))

    @property
    def yellow(self) -> int:
        return self._get_theme("yellow", (189, 131, 26))


theme = Theme()
history_manager = HistoryManager()
update = Update()
