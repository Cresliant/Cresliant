import os
import sys

import dearpygui.dearpygui as dpg
from pydantic import BaseModel

from src.corenodes.display import InputModule, OutputModule
from src.corenodes.transform import ResizeModule, RotateModule


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("../assets"), relative_path)


dpg.create_context()
dpg.create_viewport(title="Cresliant", width=1200, height=1000)

# For quick testing, load an image immediately from the disk to speed up development
width, height, channels, data = dpg.load_image(resource_path("example.png"))
# width, height, channels, data = 300, 300, 4, [0] * 300 * 300 * 4

with dpg.texture_registry():
    dpg.add_dynamic_texture(width, height, data, tag="input_image")

with dpg.font_registry():
    dpg.add_font(resource_path("Roboto-Regular.ttf"), 17, tag="font")
    dpg.bind_font("font")


File_name_text = "Image_Edit"
modules = [
    InputModule("input_image", width, height),
    ResizeModule(width, height),
    RotateModule(),
    OutputModule("input_image"),
]


class Link(BaseModel):
    source: int
    target: int
    id: int


links = []


def hide_sidebar(sender, app_data, user_data):
    pass


def link_callback(sender, app_data):
    link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    for link_ in links:
        if link_.source == app_data[0]:
            dpg.delete_item(link_.id)
            links.remove(link_)

    links.append(Link(source=app_data[0], target=app_data[1], id=int(link)))


def delink_callback(sender, app_data):
    dpg.delete_item(app_data)
    for link in links:
        if link.id == app_data:
            links.remove(link)
            break


with dpg.window(
    tag="popup_window", no_move=True, no_close=True, no_resize=True, no_collapse=True, show=False, label="Add Node"
):
    for module in modules[1:-1]:
        dpg.add_button(label=module.name, tag=module.name + "_popup", callback=module.run)


def handle_popup(_sender, app_data):
    if app_data == 1 and dpg.is_item_hovered("MainNodeEditor"):
        dpg.focus_item("popup_window")
        dpg.show_item("popup_window")
        dpg.set_item_pos("popup_window", dpg.get_mouse_pos(local=False))
    else:
        dpg.hide_item("popup_window")


with dpg.handler_registry():
    dpg.add_mouse_click_handler(button=1, callback=handle_popup)
    dpg.add_mouse_release_handler(button=0, callback=handle_popup)

with dpg.window(
    tag="Cresliant",
    menubar=True,
    no_title_bar=True,
    no_move=True,
    no_resize=True,
    no_collapse=True,
    no_close=True,
):
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            with dpg.menu(label="Filename"):
                dpg.add_input_text(
                    tag="file_name_entry_box",
                    hint=File_name_text,
                    default_value=File_name_text,
                    width=200,
                    indent=5,
                )

            with dpg.menu(tag="Preferences", label="Preferences"):
                dpg.add_combo(
                    ("PNG", "JPG"),
                    tag="export_image_type",
                    label="Export image type",
                    default_value="PNG",
                    width=75,
                    indent=8,
                )

            dpg.add_menu_item(tag="Export_Image", label="Export image")
            dpg.add_menu_item(tag="Close_app", label="Close app", callback=lambda: dpg.stop_dearpygui())

        with dpg.menu(tag="Nodes", label="Nodes"):
            for module in modules[1:]:
                dpg.add_menu_item(tag=module.name, label=module.name, callback=module.run)

        with dpg.menu(tag="About", label="About"):
            dpg.add_menu_item(tag="project_info", label="Learn more about project", enabled=False)
            dpg.add_menu_item(tag="App_Version", label="Crescial v0.1.0", enabled=False)

    dpg.add_text("Ctrl+Click to remove a link.", bullet=True)

    with dpg.node_editor(
        tag="MainNodeEditor",
        callback=link_callback,
        delink_callback=delink_callback,
        minimap=True,
        minimap_location=dpg.mvNodeMiniMap_Location_TopRight,
    ):
        modules[0].run()
        modules[-1].run()

    for module in modules[1:-1]:
        with dpg.tooltip(parent=module.name):
            dpg.add_text(module.tooltip)

    with dpg.tooltip(parent="project_info"):
        dpg.add_text("Crescial is a free and open source image editor.")
        dpg.add_text("This project is made by: ")
        dpg.add_text("FirePlank", bullet=True)
        dpg.add_text("Potatooff", bullet=True)


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Cresliant", True)
dpg.start_dearpygui()
dpg.destroy_context()
