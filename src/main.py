import dearpygui.dearpygui as dpg
from PIL import Image

from src.corenodes.display import ImageModule, OutputModule
from src.corenodes.features import ResizeModule, RotateModule

IMAGE_PATH = r"example.png"
DISPLAY_TOOLTIPS: bool = False

dpg.create_context()
img = Image.open(IMAGE_PATH)
width, height, channels, data = dpg.load_image(IMAGE_PATH)

dpg.create_viewport(title="CRESCIAL", width=1200, height=1000)

with dpg.texture_registry():
    texture_id = dpg.add_static_texture(width, height, data)  # Create image texture

File_name_text = "Image_Edit"
modules = [
    ImageModule(texture_id),
    ResizeModule(img),
    RotateModule(img),
    OutputModule(texture_id),
]


def close(sender, app_data, user_data):
    """This close the application"""
    dpg.stop_dearpygui()


def hide_sidebar(sender, app_data, user_data):
    pass


with dpg.window(
    tag="Crescial",
    menubar=True,
    no_title_bar=True,
    no_move=True,
    no_resize=True,
    no_collapse=True,
    no_close=True,
):
    # Menu bar
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
            dpg.add_menu_item(tag="Close_app", label="Close app", callback=close)

        with dpg.menu(tag="Nodes", label="Nodes"):
            for module in modules:
                dpg.add_menu_item(
                    tag=module.name, label=module.name, callback=module.run
                )

        with dpg.menu(tag="About", label="About"):
            dpg.add_menu_item(
                tag="project_info", label="Learn more about project", enabled=False
            )
            dpg.add_menu_item(tag="App_Version", label="Crescial v0.1.0", enabled=False)

    dpg.add_text("Ctrl+Click to remove a link.", bullet=True)

    with dpg.node_editor(
        tag="MainNodeEditor",
        callback=lambda sender, app_data: dpg.add_node_link(
            app_data[0], app_data[1], parent=sender
        ),
        delink_callback=lambda sender, app_data: dpg.delete_item(app_data),
        minimap=True,
        minimap_location=dpg.mvNodeMiniMap_Location_TopRight,
    ):
        ImageModule(texture_id).run("src/example.png")

    # Popups / Right click on nodes -> Click on node before right click on it

    #    with dpg.popup("Node_Output_Image"):
    #        dpg.add_button(label="Delete", callback=lambda: dpg.delete_item("Node_Output_Image"))

    if DISPLAY_TOOLTIPS:
        for module in modules:
            with dpg.tooltip(parent=module.name):
                dpg.add_text(module.tooltip)

    with dpg.tooltip(parent="project_info"):
        dpg.add_text("Crescial is a free and open source image editor.")
        dpg.add_text("This project is made by: ")
        dpg.add_text("FirePlank", bullet=True)
        dpg.add_text("Potatooff", bullet=True)


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Crescial", True)  # set window as primary
dpg.start_dearpygui()
dpg.destroy_context()
