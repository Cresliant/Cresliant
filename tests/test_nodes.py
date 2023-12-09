import dearpygui.dearpygui as dpg
import pytest
from PIL import Image

from src.editor import node_editor
from src.utils import ImageController as dpg_img
from src.utils.nodes import history_manager
from src.utils.paths import resource_path


@pytest.fixture
def init_dpg():
    dpg.create_context()
    dpg_img.set_texture_registry(dpg.add_texture_registry())

    with dpg.texture_registry():
        dpg.add_static_texture(1, 1, [0] * 1 * 1 * 4, tag="output_0")
    with dpg.window(tag="popup_window", show=False):
        for module in node_editor.modules[1:-1]:
            dpg.add_button(label=module.name, tag=module.name + "_popup", callback=module.new, indent=3, width=180)


def test_all(init_dpg):
    # Boilerplate for the app to run correctly without errors
    image = Image.open(resource_path("icon.ico"))
    with dpg.window(tag="Cresliant", show=False):
        with dpg.menu(tag="nodes", label="Nodes"):
            for module in node_editor.modules[1:]:
                dpg.add_menu_item(tag=module.name, label=module.name, callback=module.new)

        # Testing node editor
        node_editor.start()
        for module in node_editor.modules[1:-1]:
            module.new()
            assert dpg.get_item_user_data(module.name.lower() + "_0") == module
            assert isinstance(module.run(image, module.name.lower() + "_0"), Image.Image)

    # Testing history manager
    for i in range(len(history_manager.history)):
        curr = history_manager.current
        history_manager.undo()
        assert history_manager.current != curr
    for i in range(len(history_manager.history)):
        curr = history_manager.current
        history_manager.redo()
        assert history_manager.current != curr

    dpg.destroy_context()
