"""
Handle the UI for extra assets:
"""


import importlib

import os
import glob
import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon
import traceback
from ciopath.gpath_list import PathList, GLOBBABLE_REGEX


def has_letters(rhs):
    return rhs.lower().islower()


def get_module_docstring(script):
    try:
        doctring = importlib.import_module(script).__doc__
        if has_letters(doctring):
            return doctring.strip()
    except BaseException:
        pass
    return "No doctring"


def create_ui(node_attr):
    """Build static UI."""
    with AEcommon.ae_template():

        f = pm.frameLayout(lv=False, cll=False, cl=False)
        pm.rowLayout("addButtonRow",
                     numberOfColumns=3,
                     columnWidth3=(k.AE_TEXT_WIDTH, 120, 120),
                     columnAttach=((1, 'both', 0),
                                   (2, 'both', 0),
                                   (3, 'both', 0)))

        pm.text(label="")
        pm.button("addButton",
                  label="Add Scraper", height=24
                  )
        pm.button("resetButton",
                  label="Reset Defaults", height=24
                  )
        pm.setParent("..")

        pm.separator()
        pm.columnLayout("scrapersColumn", adj=True)
        pm.setParent("..")
        pm.separator()

        btn = pm.symbolButton("testAllButton",
                              image="SP_FileIcon.png", ann="Test active scrapers", width=24, height=24)

        _form_layout(
            pm.text(label=""),
            pm.text(label=""),
            pm.text(label="Test All"),
            btn,
            pm.text(label="", width=25)
        )

        pm.setParent(f)
        pm.setParent("..")

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""

    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()

    pm.button(widgets["add_button"], edit=True,
              command=pm.Callback(_on_add_btn, attr))

    pm.button(widgets["reset_button"], edit=True,
              command=pm.Callback(_on_reset_btn, attr))

    for widget in pm.columnLayout(widgets["scrapers_column"], q=True, childArray=True) or []:
        pm.deleteUI(widget)

    pm.setParent(widgets["scrapers_column"])
    for attr_element in attr:

        active_att = attr_element.attr("assetScraperActive")
        path_att = attr_element.attr("assetScraperName")

        active_ctl = pm.checkBox(label="")
        path_ctl = pm.textField()

        browse_ctl = pm.symbolButton(image="SP_DirClosedIcon.png", width=24, height=24,
                                     command=pm.Callback(_on_browse_button, attr_element, path_ctl, active_ctl))

        test_ctl = pm.symbolButton(image="SP_FileIcon.png", ann="Test this scraper", width=24, height=24,
                                   command=pm.Callback(_test_scraper, attr_element))

        del_ctl = pm.symbolButton(image="smallTrash.xpm", width=24, height=24,
                                  command=pm.Callback(_remove_scraper, attr_element))

        # arrange these controls in a formLayout. Easier than a rowLayout
        _form_layout(active_ctl, path_ctl, browse_ctl, test_ctl, del_ctl)

        pm.connectControl(active_ctl, active_att)
        pm.connectControl(path_ctl, path_att)

        _setup_script_jobs(attr_element, path_ctl)

        _active_cb_changed(active_att, path_ctl)
        _set_docstring(path_att, path_ctl)

        pm.setParent(widgets["scrapers_column"])

    pm.setParent("..")

    pm.symbolButton(widgets["test_all_button"], edit=True,  command=pm.Callback(
        _test_scraper, attr))


def _setup_script_jobs(attr_element, path_ctl):
    active_att = attr_element.attr("assetScraperActive")
    path_att = attr_element.attr("assetScraperName")

    pm.scriptJob(
        attributeChange=(
            active_att,
            pm.Callback(_active_cb_changed, active_att, path_ctl),
        ),
        parent=path_ctl,
        replacePrevious=True
    )

    pm.scriptJob(
        attributeChange=(
            path_att,
            pm.Callback(_set_docstring, path_att, path_ctl)
        ),
        parent=path_ctl
    )


def _form_layout(*widgets):
    # There must be 5 widgets.
    # we stretch the second widget.
    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", 2)
    form.attachNone(widgets[0], "right")
    form.attachForm(widgets[0], "top", 2)
    form.attachForm(widgets[0], "bottom", 2)

    form.attachControl(widgets[1], "left", 2, widgets[0])
    form.attachControl(widgets[1], "right", 2, widgets[2])
    form.attachForm(widgets[1], "top", 2)
    form.attachForm(widgets[1], "bottom", 2)

    form.attachNone(widgets[2], "left")
    form.attachControl(widgets[2], "right", 2, widgets[3])
    form.attachForm(widgets[2], "top", 2)
    form.attachForm(widgets[2], "bottom", 2)

    form.attachNone(widgets[3], "left")
    form.attachControl(widgets[3], "right", 2, widgets[4])
    form.attachForm(widgets[3], "top", 2)
    form.attachForm(widgets[3], "bottom", 2)

    form.attachNone(widgets[4], "left")
    form.attachForm(widgets[4], "right", 2)
    form.attachForm(widgets[4], "top", 2)
    form.attachForm(widgets[4], "bottom", 2)

    return form


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "add_button":  AEcommon.find_ui("addButton", parent),
        "reset_button":  AEcommon.find_ui("resetButton", parent),
        "scrapers_column":  AEcommon.find_ui("scrapersColumn", parent),
        "test_all_button":  AEcommon.find_ui("testAllButton", parent)
    }


def _on_add_btn(attr):
    script = _browse_for_script()
    if script:
        script = os.path.splitext(os.path.basename(script))[0]
        if script:
            AEcommon.next_available_element_plug(
                attr).attr("assetScraperName").set(script)


def _on_reset_btn(attr):
    """
    Reset the list of asset scrapers to factory defaults.

    In other words, reset it to the list of sdcrapers that begin with "scrape_"
    in the scripts directory of the installation. 

    attr: is a compound multi attribute holding asset scraper scripts. 

    The children of each element are: 
    * assetScraperName
    * assetScraperActive
    """
    for element in attr:
        pm.removeMultiInstance(element, b=True)

    script_path = os.path.join(
        pm.moduleInfo(
            path=True, moduleName="conductor"), "scripts"
    )
    files = sorted(glob.glob("{}/scrape_*.py".format(script_path)))
    for i, scraper in enumerate(files):
        attr[i].attr("assetScraperName").set(
            os.path.splitext(os.path.basename(scraper))[0])


def _on_browse_button(attr, path_field, active_checkbox):
    script = _browse_for_script()
    if script:
        script = os.path.splitext(os.path.basename(script))[0]
        attr.attr("assetScraperName").set(script)
        attr.attr("assetScraperActive").set(True)
        pm.textField(path_field, edit=True,   enable=True)
        pm.checkBox(active_checkbox, edit=True, value=True)
        pm.evalDeferred(pm.Callback(
            _set_docstring, attr.attr("assetScraperName"), path_field))


def _browse_for_script():
    entries = pm.fileDialog2(
        caption="Choose Script",
        okCaption="Choose",
        fileFilter="*",
        dialogStyle=2,
        fileMode=1,
        dir=pm.workspace.getPath())
    if entries:
        return entries[0]
    pm.displayWarning('No files Selected')


def _test_scraper(attr):
    """
    Display scraper execution results in the script editor. 

    Broadly speaking, scraping happens in 2 stages:
    1. Get paths from attributes (or wherever) in a compact form. At this stage, all tokens and $F4 and env vars have been resolved. They may still
       contain glob characters however: (*, ?, [, ]). These paths are objects and have metadata associated with them, such as the attribute they originated from.
    2. We glob them and deduplicate the list to generate the final file list that will be uploaded.

    This test function prints out both stages to the script editor.

    Example outpout for the xgen scraper:

    # Path objects for scrapers: [u'scrape_xgen'] # 
    {'plug': u'collection.xgFileName', 'path': u'/Volumes/xtr/gd/duck/scenes/quack_udim_xgen.0005__collection.xgen'}
    {'plug': u'foobar.xgFileName', 'path': u'/Volumes/xtr/gd/duck/scenes/quack_udim_xgen.0005__foobar.xgen'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/collectio[n]', 'key': 'xgDataPath', 'collection': 'collection'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/collectio[n]', 'key': 'xgDataPath', 'collection': 'collection'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/collection/guides.ab[c]', 'key': 'cacheFileName', 'collection': 'collection'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/collection/densit[y]', 'key': 'mask', 'collection': 'collection'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/collection/Point[s]', 'key': 'pointDir', 'collection': 'collection'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/fooba[r]', 'key': 'xgDataPath', 'collection': 'foobar'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/fooba[r]', 'key': 'xgDataPath', 'collection': 'foobar'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/foobar/guides.ab[c]', 'key': 'cacheFileName', 'collection': 'foobar'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/foobar/densit[y]', 'key': 'mask', 'collection': 'foobar'}
    {'path': '/Volumes/xtr/gd/duck/xgen/collections/foobar/Point[s]', 'key': 'pointDir', 'collection': 'foobar'}
    # Resolved paths for scrapers: [u'scrape_xgen'] # 
    /Volumes/xtr/gd/duck/scenes/quack_udim_xgen.0005__collection.xgen
    /Volumes/xtr/gd/duck/scenes/quack_udim_xgen.0005__foobar.xgen
    /Volumes/xtr/gd/duck/xgen/collections/collection
    /Volumes/xtr/gd/duck/xgen/collections/foobar
     # Missing paths for scrapers: [u'scrape_xgen'] # 
    Volumes/xtr/gd/duck/xgen/collections/some_missing
    /Volumes/xtr/gd/duck/xgen/collections/foobar_some_missing
    """
    
    node = attr.node()
    if attr.isArray():
        scripts = [attr_element.attr("assetScraperName").get(
        ) for attr_element in attr if attr_element.attr("assetScraperActive").get()]
    else:
        scripts = [attr.attr("assetScraperName").get()]
    scripts_repr = repr(scripts)
    amendments = _run_scrapers(node, scripts)
    paths = amendments["paths"]
    envs = amendments["env"]
    
    if paths:
        pm.displayInfo("Path objects for scrapers: {}".format(scripts_repr))
        for path in paths:
            pm.displayInfo(path)

        pm.displayInfo("Resolved paths for scrapers: {}".format(scripts_repr))
        path_list = PathList()
        path_list.add(*[p["path"] for p in paths])
        path_list.remove_missing()
        path_list.glob()
        for path in path_list:
            pm.displayInfo(path.fslash())

        pm.displayInfo("Paths that do not exist on disk for scrapers: {}".format(scripts_repr))
        some_exist = False
        for pathobj in paths:
            path = pathobj["path"]
            if not GLOBBABLE_REGEX.search(path) and not os.path.exists(path):
                pm.displayWarning("Not on disk: {}".format(pathobj))
                some_exist = True
        if not some_exist:
            pm.displayWarning("No missing files")
    else:
        pm.displayInfo(
            "Scrapers returned no filenames: {}".format(scripts_repr))

    if envs:
        pm.displayInfo("Env objects for scrapers: {}".format(scripts_repr))
        for env in envs:
            pm.displayInfo(repr(env))
    else:
        pm.displayInfo(
            "Scrapers returned no environment amendments: {}".format(scripts_repr))


def _run_scrapers(node, scripts):
    result = {"paths": [], "env": []}
    show_tracebacks = node.attr("showTracebacks").get()
    msg = "Please open the Asset scraper section and test individual scrapers. Remove any offending scraper entries."
    for script in scripts:
        try:
            scraper_module = importlib.import_module(script)
            try:
                reload(scraper_module)
            except:
                importlib.reload(scraper_module)
            print("script",script)
            scraper_result = scraper_module.run(node)
            if scraper_result:
                result["paths"] += scraper_result["paths"]
                result["env"] += scraper_result["env"]
        except SyntaxError:
            pm.displayError(
                "Syntax error in the scraper script: '{}'.\n{}".format(script, msg))
            if show_tracebacks:
                pm.displayError(traceback.format_exc())
            raise
        except ImportError:
            pm.displayError(
                "Can't load the script '{}' as a Python module.\n{}".format(script, msg))
            if show_tracebacks:
                pm.displayError(traceback.format_exc())
            raise
        except BaseException:
            pm.displayError(
                "Unknown problem with the script '{}'.\n{}".format(script, msg))
            if show_tracebacks:
                pm.displayError(traceback.format_exc())
            raise
    return result


def _set_docstring(attr, widget):
    script = attr.get()
    docstring = get_module_docstring(script)
    pm.control(widget, edit=True, ann=docstring)


def _active_cb_changed(attr, path_ctl):
    pm.textField(path_ctl, edit=True, enable=attr.get())


def _remove_scraper(attribute):
    pm.removeMultiInstance(attribute, b=True)
