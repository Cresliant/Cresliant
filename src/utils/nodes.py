import dearpygui.dearpygui as dpg
from pydantic import BaseModel


def find_available_pos():
    x, y = dpg.get_mouse_pos(local=False)
    return [max(0, x - 70), max(0, y - 70)]


class Link(BaseModel):
    source: int
    target: int
    id: int


class NodeParent:
    def __init__(self, update_output: callable):
        self.counter = 0
        self.update_output = update_output
        self.settings = {}
        self.protected = False

    def update_history(self, tag):
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
            item = self.history[self.index]
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
            item = self.history[self.index]
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
