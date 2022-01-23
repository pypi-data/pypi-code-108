import sys

import maya.api.OpenMaya as om
from ciocore import data as coredata
from ciomaya.lib import conductor_menu
from ciomaya.lib.nodes.conductorRender import conductorRender


def maya_useNewAPI():
    pass


def initializePlugin(obj):
    # Use "0.5.27 to cause the version to be replaced at build time."
    plugin = om.MFnPlugin(obj, "Conductor", "0.5.27", "Any")
    try:
        plugin.registerNode(
            "conductorRender",
            conductorRender.id,
            conductorRender.creator,
            conductorRender.initialize,
            om.MPxNode.kDependNode,
        )
    except:
        sys.stderr.write("Failed to register conductorRender\n")
        raise

    conductor_menu.load()

    coredata.init(product="maya-io")


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    try:
        plugin.deregisterNode(conductorRender.id)
    except:
        sys.stderr.write("Failed to deregister conductorRender\n")
        raise

    conductor_menu.unload()
