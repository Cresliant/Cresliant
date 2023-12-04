import json
import os
import sys
import webbrowser
from tkinter.filedialog import askopenfilename, asksaveasfilename

import dearpygui.dearpygui as dpg
from PIL import Image
from pydantic import BaseModel

import ImageController as dpg_img
from src.corenodes.display import InputModule, OutputModule
from src.corenodes.transform import BlurModule, ResizeModule, RotateModule


class Link(BaseModel):
    source: int
    target: int
    id: int


links = []
path = []


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("assets"), relative_path)


dpg.create_context()
dpg.create_viewport(title="Cresliant", small_icon=resource_path("icon.ico"), large_icon=resource_path("icon.ico"))

# For quick testing, load an image immediately from the disk to speed up development
pillow_image = Image.open(resource_path("example.png"))
width, height = pillow_image.size
dpg_img.set_texture_registry(dpg.add_texture_registry())

with dpg.font_registry():
    dpg.add_font(resource_path("Roboto-Regular.ttf"), 17, tag="font")
    dpg.bind_font("font")


def update_path():
    global path

    path.clear()
    for node in dpg.get_all_items():
        try:
            data_ = dpg.get_item_user_data(node)
        except SystemError:
            continue
        if data_ and "input" in str(data_).lower():
            path.append(node)
            break

    while True:
        link = dpg.get_item_info(path[-1])["children"][1][-1]
        found = False
        for link_ in links:
            if link_.source == link:
                try:
                    path.append(dpg.get_item_info(link_.target)["parent"])
                except SystemError:
                    continue

                found = True
                break

        if not found:
            break


def update_output(sender=None, app_data=None):
    if sender and app_data:
        try:
            node = dpg.get_item_info(dpg.get_item_info(sender)["parent"])["parent"]
            module = dpg.get_item_user_data(node)
        except SystemError:
            return

        module.settings[dpg.get_item_alias(node)][sender] = app_data

    try:
        output = dpg.get_item_user_data(path[-1])
    except IndexError:
        dpg.get_item_user_data("Output").viewer.load(Image.new("RGBA", dpg.get_item_user_data("Input").image.size))
        return
    if "output" not in str(output).lower():
        dpg.get_item_user_data("Output").viewer.load(Image.new("RGBA", dpg.get_item_user_data("Input").image.size))
        return

    image = Image.new("RGBA", (width, height))
    for node in path[:-1]:
        tag = dpg.get_item_alias(node)
        node = dpg.get_item_user_data(node)
        image = node.run(image, tag)

    output.viewer.load(image)
    output.image = image


modules = [
    InputModule(pillow_image, update_output),
    ResizeModule(update_output),
    RotateModule(update_output),
    BlurModule(update_output),
    OutputModule(Image.new("RGBA", pillow_image.size)),
]


def protected_node(data_):
    return "input" in str(data_).lower() or "output" in str(data_).lower()


def link_callback(sender, app_data):
    for link in links:
        if link.source == app_data[0]:
            try:
                dpg.delete_item(link.id)
            except SystemError:
                continue
            links.remove(link)

    link = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    links.append(Link(source=app_data[0], target=app_data[1], id=int(link)))

    update_path()
    update_output()


def reset(_sender=None, _app_data=None):
    for node in dpg.get_all_items():
        try:
            data_ = dpg.get_item_user_data(node)
        except SystemError:
            continue
        if data_ and not protected_node(data_):
            dpg.delete_item(node)

    links.clear()

    modules[0].new()
    modules[-1].new()

    update_path()
    update_output()


def export():
    image = dpg.get_item_user_data("Output").image
    image.save(
        asksaveasfilename(
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
            defaultextension=".png",
            initialfile="output.png",
            initialdir=os.curdir,
        )
    )


def save_project():
    data = {"nodes": {}, "links": []}
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

    for link in links:
        data["links"].append(
            {
                "source": str(dpg.get_item_user_data(dpg.get_item_info(link.source)["parent"])),
                "target": str(dpg.get_item_user_data(dpg.get_item_info(link.target)["parent"])),
            }
        )

    with open(
        asksaveasfilename(
            filetypes=[("Cresliant", "*.cresliant")],
            defaultextension=".cresliant",
            initialfile="project.cresliant",
            initialdir=os.curdir,
        ),
        "w",
    ) as file:
        file.write(json.dumps(data))


def open_project():
    try:
        data = json.load(
            open(
                askopenfilename(
                    filetypes=[("Cresliant", "*.cresliant")],
                    initialdir=os.curdir,
                )
            )
        )
    except FileNotFoundError:
        return

    reset()
    nodes = []
    for node in data["nodes"]:
        module = None
        for module_ in modules:
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
            tag = "_".join(setting.split("_")[0:-1]) + "_" + str(module.counter - 1)
            dpg.set_value(tag, data["nodes"][node]["settings"][node][setting])

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
            parent="MainNodeEditor",
        )
        links.append(Link(source=source, target=target, id=int(link)))

    update_path()
    update_output()


def delink_callback(_sender, app_data):
    dpg.delete_item(app_data)
    for link in links:
        if link.id == app_data:
            links.remove(link)
            break

    update_path()
    update_output()


def delete_nodes(_sender, _app_data):
    for node in dpg.get_selected_nodes("MainNodeEditor"):
        if not protected_node(dpg.get_item_user_data(node)):
            node_links = dpg.get_item_info(node)["children"][1]
            dpg.delete_item(node)
            for link in links:
                if link.source in node_links or link.target in node_links:
                    links.remove(link)

    update_path()
    update_output()


def delete_links(_sender, _app_data):
    for link in dpg.get_selected_links("MainNodeEditor"):
        dpg.delete_item(link)
        for link_ in links:
            if link_.id == link:
                links.remove(link_)
                break

    update_path()
    update_output()


def duplicate_nodes(_sender, _app_data):
    for node in dpg.get_selected_nodes("MainNodeEditor"):
        data_ = dpg.get_item_user_data(node)
        if not protected_node(data_):
            data_.new()


with dpg.window(
    tag="popup_window",
    no_move=True,
    no_close=True,
    no_resize=True,
    no_collapse=True,
    show=False,
    label="Add Node",
    width=200,
):
    for module in modules[1:-1]:
        dpg.add_button(label=module.name, tag=module.name + "_popup", callback=module.new, indent=3, width=180)

with dpg.window(
    tag="node_popup_window", no_move=True, no_close=True, no_resize=True, no_collapse=True, show=False, label="Settings"
):
    dpg.add_button(label="Delete node", callback=delete_nodes)
    dpg.add_button(label="Duplicate node", callback=duplicate_nodes)


def handle_shortcuts(_sender, app_data):
    if not dpg.is_key_down(dpg.mvKey_Control):
        return

    match app_data:
        case dpg.mvKey_V:
            duplicate_nodes(None, None)
        case dpg.mvKey_N:
            reset()
        case dpg.mvKey_E:
            export()
        case dpg.mvKey_S:
            save_project()
        case dpg.mvKey_O:
            open_project()
        case dpg.mvKey_Q:
            dpg.stop_dearpygui()
        case dpg.mvKey_Z:
            print("Undo")
        case dpg.mvKey_Y:
            print("Redo")


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

    dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=delete_nodes)
    dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=delete_links)

    dpg.add_key_release_handler(key=dpg.mvKey_V, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_N, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_E, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_S, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_O, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_Q, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_Z, callback=handle_shortcuts)
    dpg.add_key_release_handler(key=dpg.mvKey_Y, callback=handle_shortcuts)

    # Dev tools
    dpg.add_key_release_handler(key=dpg.mvKey_F10, callback=dpg.show_item_registry)
    dpg.add_key_release_handler(key=dpg.mvKey_F11, callback=dpg.show_style_editor)
    dpg.add_key_release_handler(key=dpg.mvKey_F12, callback=dpg.show_metrics)


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
        with dpg.menu(tag="file", label="File"):
            dpg.add_menu_item(tag="new", label="New Project", shortcut="Ctrl+N", callback=reset)
            dpg.add_menu_item(tag="open", label="Open Project...", shortcut="Ctrl+O", callback=open_project)
            dpg.add_separator()
            dpg.add_menu_item(tag="save", label="Save Project...", shortcut="Ctrl+S", callback=save_project)
            dpg.add_menu_item(tag="export", label="Export Output...     ", shortcut="Ctrl+E", callback=export)
            dpg.add_separator()
            dpg.add_menu_item(tag="close", label="Quit", shortcut="Ctrl+Q", callback=dpg.stop_dearpygui)

        with dpg.menu(tag="edit", label="Edit"):
            dpg.add_menu_item(label="Undo    ", tag="undo", shortcut="Ctrl+Z")
            dpg.add_menu_item(label="Redo    ", tag="redo", shortcut="Ctrl+Y")

        with dpg.menu(tag="nodes", label="Nodes"):
            for module in modules[1:]:
                dpg.add_menu_item(tag=module.name, label=module.name, callback=module.new)

        with dpg.menu(tag="about", label="About"):
            dpg.add_menu_item(
                tag="github",
                label="View it on Github",
                callback=lambda: webbrowser.open("https://github.com/Cresliant/Cresliant"),
            )
            dpg.add_separator()
            dpg.add_menu_item(tag="version", label="Cresliant v0.1.0", enabled=False)

    dpg.add_text("Ctrl+Click to remove a link.", bullet=True)

    with dpg.node_editor(
        tag="MainNodeEditor",
        callback=link_callback,
        delink_callback=delink_callback,
        minimap=True,
        minimap_location=dpg.mvNodeMiniMap_Location_TopRight,
    ):
        modules[0].new()
        modules[-1].new()

    for module in modules[1:-1]:
        with dpg.tooltip(parent=module.name):
            dpg.add_text(module.tooltip)
        with dpg.tooltip(parent=module.name + "_popup"):
            dpg.add_text(module.tooltip)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.maximize_viewport()
dpg.set_primary_window("Cresliant", True)
dpg.start_dearpygui()
dpg.destroy_context()
