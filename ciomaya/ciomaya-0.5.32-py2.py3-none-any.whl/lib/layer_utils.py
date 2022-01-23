import pymel.core as pm
from contextlib import contextmanager


@contextmanager
def layer_context(layer):
    """Perform some ops in the context of the given render layer"""
    current_layer = pm.editRenderLayerGlobals(q=True, currentRenderLayer=True)
    pm.editRenderLayerGlobals(currentRenderLayer=layer)
    yield
    pm.editRenderLayerGlobals(currentRenderLayer=current_layer)


def get_layer_name(layer):
    layer = pm.PyNode(layer)
    name = layer.name()
    if name == "defaultRenderLayer" or name == "masterLayer":
        return "masterLayer"
    conns = layer.attr("message").connections(d=True, s=False, et=True, t="renderSetupLayer")
    if not conns:
        return name
    return conns[0].name()


def get_current_layer_name():
    return get_layer_name(pm.editRenderLayerGlobals(q=True, currentRenderLayer=True))


def get_renderable_legacy_layers():
    attr = pm.PyNode("renderLayerManager").attr("renderLayerId")
    return [l for l in attr.connections() if l.attr("renderable").get()]
