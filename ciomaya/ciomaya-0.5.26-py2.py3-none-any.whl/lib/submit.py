"""
Submit.

"""
import json
import os
import sys
import traceback
from contextlib import contextmanager

import pymel.core as pm
from ciocore import conductor_submit
from ciotemplate.expander import Expander
from ciomaya.lib import const as k
from ciomaya.lib import layer_utils, validation, window, renderman_path_utils
from ciocore.validator import ValidationError


@contextmanager
def full_output(node):
    task_limit = node.attr("taskLimit").get()
    do_scrape = node.attr("doScrape").get()
    node.attr("taskLimit").set(-1)
    node.attr("doScrape").set(True)
    yield
    node.attr("taskLimit").set(task_limit)
    node.attr("doScrape").set(do_scrape)


@contextmanager
def transient_save(filepath, cleanup=True):
    """
    Save the scene and clean up afterwards.

    Do the Save function in the context of adjusted paths (currently just renderman paths).
    This effectively linuxifies the scene file.

    Args: filepath (string): cleanup (bool, optional): whether or not to delete the saved file
        afterward. Defaults to True.
    """
    original = pm.sceneName()
    with renderman_path_utils.strip_drive():
        pm.saveAs(filepath)
    try:
        yield
    finally:
        pm.renameFile(original)
        if cleanup:
            try:
                os.remove(filepath)
            except OSError:
                pm.displayWarning("Couldn't cleanup file: {}".format(filepath))


def valid(node):

    try:
        validation.run(node)
    except ValidationError as ex:
        pm.displayWarning(str(ex))
        return False
    return True


def submit(node):
    """
    Submit job based on either an autoaved file or a manually saved file.
    """
    filepath = pm.sceneName()
    if filepath and node.attr("autosave").get():
        filepath = _resolve_autosave_template(node)
        if filepath:
            cleanup = should_cleanup_autosave(node)
            if valid(node):
                with transient_save(filepath, cleanup=cleanup):
                    handle_submissions(node)
            return
        else:
            pm.warning("No valid autosave template. Opening file browser for manual save.")

    # NOTE Consider removing the manual file save option, because the actual file may have certain
    # adjustments in order for it to work on Linux. Those adjustments may prevent it from working on
    # Windows. This is okay for autosave, but the user may assume that a manually saved file should
    # be able to be opened again on the host machine.
    if pm.isModified():
        filepath = browse_save_as()
        if not filepath:
            pm.warning("No file Selected")
            return
        with renderman_path_utils.strip_drive():
            pm.saveAs(filepath)

    if valid(node):
        handle_submissions(node)

def should_cleanup_autosave(node):
    node = pm.PyNode(node)
    if not node.attr("cleanupAutosave").get():
        return False
    if node.attr("useUploadDaemon").get():
        return False
    autosave_template = node.attr("autosaveTemplate").get()
    if autosave_template and autosave_template.lower().strip() == "<scene>":
        return False
    return True

def handle_submissions(node):
    submissions = get_submissions(node)
    responses = do_submissions(submissions, node)
    window.show_submission_responses(responses)


def get_submissions(node):

    submissions = []
    layer_policy = node.attr("renderLayers").get()

    if layer_policy == k.CURRENT_LAYER:
        submissions.append(get_submission(node))
    else:
        for layer in layer_utils.get_renderable_legacy_layers():
            with layer_utils.layer_context(layer):
                submissions.append(get_submission(node))
    return list(filter(None, submissions))


def do_submissions(submissions, node):
    results = []
    show_tracebacks = node.attr("showTracebacks").get()
    for submission in submissions:
        try:
            remote_job = conductor_submit.Submit(submission)
            response, response_code = remote_job.main()
            results.append({"code": response_code, "response": response})
        except BaseException as ex:
            if show_tracebacks:
                msg = traceback.format_exc()
            else:
                msg = str(ex)
            pm.displayError(msg)
            results.append({"code": "undefined", "response": msg})

    return results


def _resolve_autosave_template(node):
    """
    Generate a full filename to save automatically.
    """
    ws = pm.Workspace()

    template = node.attr("autosaveTemplate").get()
    msg = "Invalid autosave template. Saving manually."
    if not (template and template.strip()):
        pm.displayWarning(msg)
        return

    full_scene_path = pm.sceneName()
    if full_scene_path:
        directory = os.path.dirname(full_scene_path)
        filename = os.path.basename(full_scene_path)
    else:
        filename = "untitled.ma"
        try:
            directory = ws.fileRules.get("mayaAscii").split(":")[0]
            directory = ws.expandName(directory)
        except Exception:
            directory = ws.expandName("scenes")

    context = {"Scene": filename, "scene": filename}
    expander = Expander(**context)
    resolved_name = expander.evaluate(template)
    if not resolved_name:
        pm.displayWarning(msg)
        return

    if not os.path.isabs(resolved_name):
        resolved_name = os.path.join(directory, resolved_name)

    return resolved_name


def browse_save_as():
    filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

    entries = pm.fileDialog2(
        caption="Save File As",
        okCaption="Save As",
        fileFilter=filters,
        dialogStyle=2,
        fileMode=0,
        dir=os.path.dirname(pm.sceneName()),
    )

    if entries:
        return entries[0]


def get_submission(node):
    out_attr = pm.PyNode(node).attr("output")
    with full_output(node):
        pm.dgdirty(out_attr)
        result = out_attr.get()
        if result:
            return json.loads(result)
