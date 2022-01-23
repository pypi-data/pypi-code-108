import pymel.core as pm


def ensure_connections(node):
    """
    Ensure all required attributes are connected.

    Some old scenes may not have all these connections in place. This is called on createNode, and
    checked when connecting to Conductor.
    """
    pairs = [
        (pm.Attribute("defaultRenderGlobals.startFrame"), node.attr("startFrame")),
        (pm.Attribute("defaultRenderGlobals.endFrame"), node.attr("endFrame")),
        (pm.Attribute("defaultRenderGlobals.byFrameStep"), node.attr("byFrame")),
        (pm.Attribute("defaultRenderGlobals.animation"), node.attr("animation")),
        (pm.Attribute("defaultRenderGlobals.currentRenderer"), node.attr("currentRenderer")),
        (pm.Attribute("renderLayerManager.currentRenderLayer"), node.attr("currentRenderLayer")),
        (pm.Attribute("time1.outTime"), node.attr("currentFrame")),
    ]
    for src, dest in pairs:
        if not pm.isConnected(src, dest):
            pm.displayInfo("connectAttr: {} {}".format(src, dest))
            src >> dest


def calc_dest_path():
    ws = pm.Workspace()
    try:
        imagesdir = pm.workspace.fileRules.get("images")
    except Exception:
        imagesdir = "images"
    return ws.expandName(imagesdir)
