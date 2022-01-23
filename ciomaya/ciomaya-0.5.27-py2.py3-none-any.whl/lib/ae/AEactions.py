"""
Handle the UI for actions:

"""
import pymel.core as pm
from ciocore import data as coredata

from ciomaya.lib import node_utils
from ciomaya.lib.ae import AEcommon
from ciomaya.lib import const as k
from ciomaya.lib import submit
from ciomaya.lib import validation
from ciocore.validator import ValidationError
from ciomaya.lib import asset_cache


def create_ui(node_attr):
    """Build row for action buttons."""
    with AEcommon.ae_template():
        but_width = k.AE_TOTAL_WIDTH / 6
        top = pm.frameLayout(label="Shelf", cll=False, cl=False)
        pm.rowLayout(
            numberOfColumns=3,
            cw3=(but_width, but_width, but_width),
            columnAttach3=("left", "left", "left"),
        )

        pm.iconTextButton(
            "connectButton",
            label="Reconnect",
            ann="Reconnect to Conductor and fetch account data",
            w=but_width,
            style="iconAndTextVertical",
            en=True,
            image1="ConductorConnect_30x30.png",
        )

        pm.iconTextButton(
            "submitButton",
            label="Submit",
            ann="Submit Job",
            w=but_width,
            style="iconAndTextVertical",
            en=False,
            image1="ConductorSubmit_30x30.png",
        )

        pm.iconTextButton(
            "validateButton",
            label="Validate",
            ann="Validate Only",
            w=but_width,
            style="iconAndTextVertical",
            image1="ConductorShow_30x30.png",
        )

        pm.setParent(top)
        pm.setParent("..")

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    widgets = _get_widgets()
    node = pm.Attribute(node_attr).node()
    pm.iconTextButton(
        widgets["connect"], edit=True, command=pm.Callback(_on_connect, widgets, node, force=True)
    )
    pm.iconTextButton(widgets["submit"], edit=True, en=False, command=pm.Callback(on_submit, node))

    pm.iconTextButton(widgets["validate"], edit=True, command=pm.Callback(on_validate, node))

    pm.evalDeferred(pm.Callback(_on_connect, widgets, node))


def _on_connect(widgets, node, force=False):
    """
    Connect to Conductor in order to access users account data.

    Also make sure this node is wired up to defaultRenderGlobals.

    NOTE: The word connection has 2 meanings here. node connections are nothing to do with the
    connection to Maya. This just happens to be the best place to deal with both of them.

    """
    node_utils.ensure_connections(node)

    use_fixtures = node.attr("useFixtures").get()

    fixtures_dir = node.attr("fixturesDirectory").get() if use_fixtures else None
    coredata.set_fixtures_dir(fixtures_dir)

    try:
        coredata.data(force=force)
    except BaseException as ex:
        pm.displayError(str(ex))
        pm.displayWarning(
            "Try again after deleting your credentials file (~/.config/conductor/credentials)"
        )
    set_enabled_state(widgets)

    if force:
        # If the Reconnect button was clicked, then also force refresh in order to tell the
        # inst_types, software, and projects rebuild themselves based on new data.
        pm.mel.openAEWindow()


def _get_widgets(parent=None):
    """Widgets are children of the named top layout we constructed.

    If no parent given, then we must be "in" the parent
    that contains the expected widgets.
    """
    if not parent:
        parent = pm.setParent(q=True)

    return {
        "submit": AEcommon.find_ui("submitButton", parent),
        "connect": AEcommon.find_ui("connectButton", parent),
        "validate": AEcommon.find_ui("validateButton", parent),
    }


def set_enabled_state(widgets):
    can_submit = coredata.valid()
    pm.iconTextButton(widgets["submit"], edit=True, en=can_submit)


def on_submit(node):
    asset_cache.clear()
    submit.submit(node)


def on_validate(node):
    asset_cache.clear()
    try:
        validation.run(node, dry_run=True)
    except ValidationError as ex:
        pm.displayWarning(str(ex))
