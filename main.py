import os
import sys
import webbrowser

import dearpygui.dearpygui as dpg
from pydantic import BaseModel

from src.corenodes.display import InputModule, OutputModule
from src.corenodes.transform import BlurModule, ResizeModule, RotateModule


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("assets"), relative_path)


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
    BlurModule(),
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
    for link in links:
        if link.source == app_data[0]:
            dpg.delete_item(link.id)
            links.remove(link)

    link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    links.append(Link(source=app_data[0], target=app_data[1], id=int(link)))
    find_path()


def find_path():
    path = []

    for link in links:
        if dpg.get_item_user_data(link.source) == "input":
            path.append(dpg.get_item_info(link.source)["parent"])
            path.append(dpg.get_item_info(link.target)["parent"])
            break

    while True:
        source_found = False
        for link in links:
            print(dpg.get_item_info(link.target)["parent"], dpg.get_item_info(link.source)["parent"])
            if link.source == path[-1]:
                path.append(dpg.get_item_info(link.target)["parent"])
                source_found = True

        if not source_found:
            break

    print(path)
    print(links)


def delink_callback(sender, app_data):
    dpg.delete_item(app_data)
    for link in links:
        if link.id == app_data:
            links.remove(link)
            break


def delete_nodes(sender, app_data):
    for node in dpg.get_selected_nodes("MainNodeEditor"):
        dpg.delete_item(node)


def duplicate_nodes(sender, app_data):
    for node in dpg.get_selected_nodes("MainNodeEditor"):
        dpg.get_item_user_data(node).run()


with dpg.window(
    tag="popup_window",
    no_move=True,
    no_close=True,
    no_resize=True,
    no_collapse=True,
    show=False,
    label="Options",
    width=250,
    height=300,
):
    with dpg.menu(label="Add Node", indent=5):
        for module in modules[1:-1]:
            dpg.add_button(label=module.name, tag=module.name + "_popup", callback=module.run, indent=3, width=200)

with dpg.window(
    tag="node_popup_window", no_move=True, no_close=True, no_resize=True, no_collapse=True, show=False, label="Settings"
):
    dpg.add_button(label="Delete node", callback=delete_nodes)
    dpg.add_button(label="Duplicate node", callback=duplicate_nodes)


def handle_popup(_sender, app_data):
    if app_data == 1 and dpg.is_item_hovered("MainNodeEditor"):
        if len(dpg.get_selected_nodes("MainNodeEditor")) != 0:
            dpg.focus_item("node_popup_window")
            dpg.show_item("node_popup_window")
            dpg.set_item_pos("node_popup_window", dpg.get_mouse_pos(local=False))
            return

        dpg.focus_item("popup_window")
        dpg.show_item("popup_window")
        dpg.set_item_pos("popup_window", dpg.get_mouse_pos(local=False))
    else:
        dpg.hide_item("popup_window")
        dpg.hide_item("node_popup_window")


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
            dpg.add_separator()
            with dpg.menu(tag="Preferences", label="Preferences"):
                dpg.add_combo(
                    ("PNG", "JPG"),
                    tag="export_image_type",
                    label="Export image type",
                    default_value="PNG",
                    width=75,
                    indent=8,
                )

            dpg.add_menu_item(tag="export", label="Export image")
            dpg.add_menu_item(tag="close", label="Close app", callback=lambda: dpg.stop_dearpygui())

        with dpg.menu(tag="Edit", label="Edit"):
            dpg.add_button(label="Undo", tag="undo_button", enabled=False, width=150)
            dpg.add_button(label="Redo", tag="redo_button", enabled=False, width=150)
            dpg.add_separator()

        with dpg.menu(tag="Nodes", label="Nodes"):
        with dpg.menu(tag="nodes", label="Nodes"):
            for module in modules[1:]:
                dpg.add_menu_item(tag=module.name, label=module.name, callback=module.run)

        with dpg.menu(tag="about", label="About"):
            dpg.add_menu_item(
                tag="github",
                label="View it on Github",
                callback=lambda: webbrowser.open("https://github.com/Cresliant/Cresliant"),
            )
            dpg.add_menu_item(tag="app_version", label="Cresliant v0.1.0", enabled=False)

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


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Cresliant", True)
dpg.start_dearpygui()
dpg.destroy_context()
