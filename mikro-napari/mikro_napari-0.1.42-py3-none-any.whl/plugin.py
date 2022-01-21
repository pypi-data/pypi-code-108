from mikro_napari.widgets.main_widget import ArkitektWidget
from napari_plugin_engine import napari_hook_implementation

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return ArkitektWidget, {"area": "left", "name": "Arkitekt"}
