
try:
    import pymel.core as pm
except ModuleNotFoundError:
    import maya.cmds as mc
    help_url = "https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-2AA5EFCE-53B1-46A0-8E43-4CD0B2C72FB4-htm.html"
    msg = "PyMEL not installed. The Conductor Plugin requires PyMEL. Please follow the instructions at the link below to install it. Alternatively, reinstall Maya and make sure the PyMEL option is selected." 
    mc.warning(msg)
    mc.warning(help_url)
    raise

import os
import glob
import webbrowser
from ciomaya.lib import window
from ciomaya.lib import software
from ciomaya.lib import const as k
from ciomaya.lib import node_utils

MAYA_PARENT_WINDOW = "MayaWindow"
CONDUCTOR_MENU = "ConductorMenu"
CONDUCTOR_DOCS = "https://docs.conductortech.com/"
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
DEFAULT_LOG_LEVEL = LOG_LEVELS[2]


def unload():

    if pm.menu(CONDUCTOR_MENU, q=True, exists=True):
        pm.menu(CONDUCTOR_MENU, e=True, deleteAllItems=True)
        pm.deleteUI(CONDUCTOR_MENU)


def load():
    unload()
    ConductorMenu()


class ConductorMenu(object):
    def __init__(self):
        if not pm.about(batch=True):
            pm.setParent(MAYA_PARENT_WINDOW)
            self.menu = pm.menu(
                CONDUCTOR_MENU,
                label="Conductor",
                tearOff=True,
                pmc=pm.Callback(self.post_menu_command),
            )
            self.jobs_menu = pm.menuItem(label="Submitter", subMenu=True)

            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)
            
            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)

            self.help_menu = pm.menuItem(
                label="Help", command=pm.Callback(webbrowser.open, CONDUCTOR_DOCS, new=2)
            )
            self.about_menu = pm.menuItem(label="About", command=pm.Callback(window.show_about))


    def post_menu_command(self):
        """
        Build the Select/Create submenu just before the menu is opened.
        """
        pm.setParent(self.jobs_menu, menu=True)
        pm.menu(self.jobs_menu, edit=True, deleteAllItems=True)
        for j in pm.ls(type="conductorRender"):

            pm.menuItem(label="Select {}".format(str(j)), command=pm.Callback(select_and_show, j))
        pm.menuItem(divider=True)

        pm.menuItem(label="Create", command=pm.Callback(create_render_node))
        pm.setParent(self.menu, menu=True)

def create_render_node():
    node = pm.createNode("conductorRender")

    setup_render_node(node)
    select_and_show(node)


def select_and_show(node):
    pm.select(node)

    if not pm.mel.isAttributeEditorRaised():
        pm.mel.openAEWindow()


def setup_render_node(node):
    dest_path = node_utils.calc_dest_path()

    node.attr("destinationDirectory").set(dest_path)
    node.attr("hostSoftware").set(software.detect_host())

    # TODO: Combine with sw detect code in AEsoftware
    i = 0
    for plugin_software_name in [
        sw
        for sw in [
            software.detect_mtoa(),
            software.detect_rfm(),
            software.detect_vray(),
            software.detect_redshift(),
            software.detect_yeti(),
        ]
        if sw
    ]:
        node.attr("pluginSoftware")[i].set(plugin_software_name)
        i += 1

    node.attr("taskTemplate").set(k.DEFAULT_TEMPLATE)
    node.attr("autosaveTemplate").set(k.DEFAULT_AUTOSAVE_TEMPLATE)
    node.attr("instanceTypeName").set(k.DEFAULT_INSTANCE_TYPE)
    node.attr("title").set(k.DEFAULT_TITLE)

    node.attr("customRange").set("1-10")
    node.attr("scoutFrames").set("auto:3")

    node_utils.ensure_connections(node)

    # asset scrapers
    script_path = os.path.join(pm.moduleInfo(path=True, moduleName="conductor"), "scripts")

    files = sorted(glob.glob("{}/scrape_*.py".format(script_path)))
    for i, scraper in enumerate(files):
        scraper_name = os.path.splitext(os.path.basename(scraper))[0]
        node.attr("assetScrapers[{:d}].assetScraperName".format(i)).set(scraper_name)
