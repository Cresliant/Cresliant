import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from core import *
from PIL import Image

img = Image.open(r"PATH_TO_AN_IMAGE.png")
TOOLTIPS_DISPLAY: bool = False

dpg.create_context()
width, height, channels, data = dpg.load_image(r"PATH_TO_AN_IMAGE.png")

print(img.size)


dpg.create_viewport(
    title='CRESCIAL', 
    width=1200,
    height = 1000
)




with dpg.texture_registry():
    texture_id = dpg.add_static_texture(width, height, data) # Create image texture



File_name_text: str = "Image_Edit"

tooltips_text: list[str, str] = [
    ("Resize_tool", "Resize tool to modify image size"), 
    ("Rotate_tool", "Rotate tool for rotating the image"), 
    ("Blur_tool", "Blur tool for bluring image ;)"), 
    ("Zoom_tool", "Zoom tool for zooming area from your image ;)"),
    ("Preferences", "This are settings for the image viewer."),
    ("export_image_type", "Choose the default image type to export:\nPNG is recommended for better quality.\nJPG is recommended for smaller file size."),
    ("Export_Image", "Save / Export image to default location"),
    ("Close_app", "You are exiting the application!"),
    ("Image_Package", "List of tools to edit your generated image!")
]



def hide_sidebar(sender, app_data, user_data):
    ...

def Resize_tool_handler(sender, app_data, user_data): ...


def Rotate_tool_handler(sender, app_data, user_data): ...

def CloseApp_Handler(sender, app_data, user_data):
    dpg.stop_dearpygui()


def Zoom_tool_handler(sender, app_data, user_data):
    ...

def Blur_tool_handler(sender, app_data, user_data):
    ...

def Export_image_handler(sender, app_data, user_data): ...



with dpg.window(
    tag="Crescial", 
    menubar=True,
    no_title_bar=True,
    no_move = True,
    no_resize = True,
    no_collapse = True,
    no_close = True
    ):
    
    # Menu bar
    with dpg.menu_bar():

        with dpg.menu(label="File"):

            with dpg.menu(label="Filename"):
                dpg.add_input_text(tag="file_name_entry_box", hint=File_name_text, default_value=File_name_text, width=200, indent=5)
            
            with dpg.menu(tag="Preferences", label="Preferences"):
                dpg.add_combo(("PNG", "JPG"), tag="export_image_type", label="Export image type", default_value="PNG", width=75, indent=8)

            dpg.add_menu_item(tag="Export_Image", label="Export image")
            dpg.add_menu_item(tag="Close_app", label="Close app", callback=CloseApp_Handler)

        

        with dpg.menu(tag="Image_Package", label="Image Tools"):
            dpg.add_menu_item(tag="Resize_tool", label="Resize", callback=Resize_tool_handler)
            dpg.add_menu_item(tag="Rotate_tool", label="Rotate", callback=Rotate_tool_handler)
            dpg.add_menu_item(tag="Blur_tool", label="Blur", callback=Blur_tool_handler)
            dpg.add_menu_item(tag="Zoom_tool", label="Zoom", callback=Zoom_tool_handler)
            #dpg.add_menu_item(tag="Resize_tool", label="")

        with dpg.menu(tag="About_Informations", label="About"): 
            dpg.add_menu_item(tag="project_info", label="Learn more about project")
            dpg.add_menu_item(tag="App_Version", label="Crescial v0.1.0")

    if TOOLTIPS_DISPLAY:
        # Tooltips loader
        for i in tooltips_text:
            with dpg.tooltip(i[0]):
                dpg.add_text(i[1])

    


    dpg.add_text("Ctrl+Click to remove a link.", bullet=True)

    with dpg.node_editor(callback=lambda sender, app_data: dpg.add_node_link(app_data[0], app_data[1], parent=sender), 
                            delink_callback=lambda sender, app_data: dpg.delete_item(app_data), minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight):

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
                dpg.add_slider_int(tag="Resize_Percentage", label="Resize in percentage", width=150, default_value=0, max_value=100, min_value=0)



        with dpg.node(label="Image result", pos=[500, 20]):
            with dpg.node_attribute() as Image_result:
                ...
                #dpg.add_image_button(texture_id,  tag="result_image_button", width=400, height=400)



    #dpg.add_image(texture_id)
        



dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Crescial", True)
dpg.start_dearpygui()
dpg.destroy_context()
