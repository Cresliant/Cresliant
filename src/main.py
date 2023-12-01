import dearpygui.dearpygui as dpg
from PIL import Image

from src.coremodules.transform import ResizeModule, RotateModule
from src.coremodules.input import ImageModule

IMAGE_PATH = r"example.png"
img = Image.open(IMAGE_PATH)

dpg.create_context()
width, height, channels, data = dpg.load_image(IMAGE_PATH)

dpg.create_viewport(
    title='CRESCIAL',
    width=1200,
    height=1000
)

with dpg.texture_registry():
    texture_id = dpg.add_static_texture(width, height, data)  # Create image texture

File_name_text = "Image_Edit"
modules = [
    ImageModule,
    ResizeModule,
    RotateModule
]


def hide_sidebar(sender, app_data, user_data):
    pass


def close(sender, app_data, user_data):
    dpg.stop_dearpygui()


with dpg.window(
        tag="Crescial",
        menubar=True,
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        no_collapse=True,
        no_close=True
):
    # Menu bar
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            with dpg.menu(label="Filename"):
                dpg.add_input_text(tag="file_name_entry_box", hint=File_name_text, default_value=File_name_text,
                                   width=200, indent=5)

            with dpg.menu(tag="Preferences", label="Preferences"):
                dpg.add_combo(("PNG", "JPG"), tag="export_image_type", label="Export image type", default_value="PNG",
                              width=75, indent=8)

            dpg.add_menu_item(tag="Export_Image", label="Export image")
            dpg.add_menu_item(tag="Close_app", label="Close app", callback=close)

        with dpg.menu(tag="Modules", label="Modules"):
            for module in modules:
                dpg.add_menu_item(tag=module.name, label=module.name, callback=module.run)

        with dpg.menu(tag="About", label="About"):
            dpg.add_menu_item(tag="project_info", label="Learn more about project", enabled=False)
            dpg.add_menu_item(tag="App_Version", label="Crescial v0.1.0", enabled=False)

    # Tooltips
    with dpg.tooltip(parent="project_info"):
        dpg.add_text("Crescial is a free and open source image editor.")
        dpg.add_text("This project is made by: ")
        dpg.add_text("FirePlank", bullet=True)
        dpg.add_text("Potatooff", bullet=True)

    for module in modules:
        with dpg.tooltip(parent=module.name):
            dpg.add_text(module.tooltip)

    dpg.add_text("Ctrl+Click to remove a link.", bullet=True)

    with dpg.node_editor(callback=lambda sender, app_data: dpg.add_node_link(app_data[0], app_data[1], parent=sender),
                         delink_callback=lambda sender, app_data: dpg.delete_item(app_data), minimap=True,
                         minimap_location=dpg.mvNodeMiniMap_Location_TopRight):

        with dpg.node(label="Default image", pos=[10, 10]):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_image_button(texture_id, tag="default_image_button", width=400, height=400)

        with dpg.node(label="Resize image", pos=[500, 20]):
            with dpg.node_attribute() as Resize_image:
                dpg.add_input_int(tag="x_size", label="x", width=100)
                dpg.add_input_int(tag="y_size", label="y", width=100)
                dpg.add_input_int(tag="z_size", label="z", width=100, default_value=img.size[0])
                dpg.add_input_int(tag="w_size", label="w", width=100, default_value=img.size[1])

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_slider_int(tag="Resize_Percentage", label="Resize in percentage", width=150, default_value=0,
                                   max_value=100, min_value=0)

        with dpg.node(label="Image result", pos=[500, 200]):
            with dpg.node_attribute() as Image_result:
                dpg.add_image_button(texture_id, tag="result_image_button", width=400, height=400)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Crescial", True)
dpg.start_dearpygui()
dpg.destroy_context()
