import dearpygui.dearpygui as dpg


def find_available_pos() -> list[int]:
    """
    Finds an available position for a new node that is not overlapping with any other node
    """

    # TODO: Implement this function
    return [0, 0]


class Theme:
    def __init__(self):
        self._cache = {}

    def _get_theme(self, color_name, color_value):
        cached = self._cache.get(color_name)
        if cached is not None:
            return cached

        with dpg.theme() as theme_id:
            with dpg.theme_component(0):
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
