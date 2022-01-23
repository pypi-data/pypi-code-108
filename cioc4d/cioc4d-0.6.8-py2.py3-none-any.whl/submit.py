import c4d
import os
import json
from contextlib import contextmanager
from ciocore import conductor_submit
from ciocore import config

import traceback
from ciocore.validator import Validator, ValidationError
from cioc4d import validation
from cioc4d import const as k
from cioc4d import utils

try:
    from urllib import parse
except ImportError:
    import urlparse as parse


SAVE_AS_DIALOG = 12218


@contextmanager
def transient_save(filename, cleanup=True):
    """
    Do something after saving a file.
    """

    doc = c4d.documents.GetActiveDocument()
    originalname = doc.GetDocumentName()
    try:
        docpath = doc.GetDocumentPath()
        filepath = os.path.join(docpath, filename)
        doc.SetDocumentName(filename)
        c4d.documents.SaveDocument(
            doc, filepath, saveflags=c4d.SAVEDOCUMENTFLAGS_AUTOSAVE, format=c4d.FORMAT_C4DEXPORT
        )
        yield

        if cleanup:
            try:
                os.remove(filepath)
            except OSError:
                c4d.WriteConsole("Couldn't cleanup file: {}\n".format(filepath))
    except BaseException:
        c4d.WriteConsole("Submission failed.\n")
        raise
    finally:
        doc.SetDocumentName(originalname)

def valid(dialog):
    try:
        validation.run(dialog)
    except ValidationError as ex:
        c4d.WriteConsole(str(ex))
        c4d.WriteConsole("\n")
        return False
    return True


def submit(dialog):

    filepath, cleanup = _resolve_autosave_template(dialog)
    if filepath:
        with transient_save(filepath, cleanup=cleanup):
            handle_submissions(dialog)
        return

    if needs_save():
        c4d.CallCommand(SAVE_AS_DIALOG)
    if needs_save():
        return

    handle_submissions(dialog)


def needs_save():
    doc = c4d.documents.GetActiveDocument()
    return doc.GetChanged() or "" == doc.GetDocumentPath()


def _resolve_autosave_template(dialog):
    """
    Generate a filename to save and determine whether to cleanup after.
    
    Use c4d's own tokens to generate the name.

    We dont cleanup in any of the following situations:
    1. Cleanup is turned off.
    2. Upload daemon is on.
    3. The autosave name resolves to the scene name.
    """

    autosave_widget = dialog.section("AutosaveSection").widget
    do_autosave = autosave_widget.get_visible()
    if not do_autosave:
        return (None, None)
    document = c4d.documents.GetActiveDocument()
    if not document.GetDocumentPath():
        c4d.WriteConsole("Can't determine document path. Please save manually.\n")
        return (None, None)

    template = autosave_widget.get_value()

    rpd = utils.rpd()
    
    try:
        resolved_name = c4d.modules.tokensystem.StringConvertTokens(template, rpd)
    except SystemError:
        resolved_name = "unknown"


    if any(c in resolved_name for c in ["$", "/", "\\"]):
        c4d.WriteConsole("Invalid autosave template. Please fix or save manually.\n")
        return (None, None)

    if not resolved_name.endswith(".c4d"):
        resolved_name = "{}.c4d".format(resolved_name)
        
    cleanup = (
        autosave_widget.get_extra_check_value()
        and (not dialog.section("UploadOptionsSection").use_daemon_widget.get_value())
        and (not document.GetDocumentName() == resolved_name)
    )

    return (resolved_name, cleanup)


def handle_submissions(dialog):
    submission = dialog.calculate_submission(with_assets=True)
    if valid(dialog):
        response = do_submission(dialog, submission)
        show_submission_response(dialog, response)


def do_submission(dialog, submission):

    show_tracebacks = dialog.section("DiagnosticsSection").widget.get_value()

    try:
        remote_job = conductor_submit.Submit(submission)
        response, response_code = remote_job.main()
        return {"code": response_code, "response": response}
    except BaseException as ex:
        if show_tracebacks:
            msg = traceback.format_exc()
        else:
            msg = ex.message
        c4d.WriteConsole("{}\n".format(msg))

        return {"code": "undefined", "response": msg}


def show_submission_response(dialog, response):
    cfg = config.config().config
    if response.get("code") <= 201:
        # success
        success_uri = response["response"]["uri"].replace("jobs", "job")
        job_url = parse.urljoin(cfg["auth_url"], success_uri)
        job_id = success_uri.split("/")[-1]

        c4d.WriteConsole("Submission result {}\n".format("*"*30))
        c4d.WriteConsole("Use this URL to monitor your Conductor job:\n{}\n".format(job_url))

        downloader_message = "If you plan on using the command-line downloader to retrieve\n"
        downloader_message += "your files when they are done, then paste the following\n"
        downloader_message += "string into the command prompt:\n"
        c4d.WriteConsole(downloader_message)

        location = (dialog.section("LocationSection").widget.get_value() or "").strip()
        if location:
            c4d.WriteConsole("\n'{}' downloader --location '{}' --job_id {}\n".format(k.CONDUCTOR_COMMAND_PATH, location, job_id))
        else:
            c4d.WriteConsole("\"{}\" downloader --job_id {}\n".format(k.CONDUCTOR_COMMAND_PATH, job_id))

        c4d.gui.MessageDialog("Success: {}\n\nPlease see the console for download instructions".format(job_url))

        return

    c4d.gui.MessageDialog("Failure: {}".format(str(response["response"])))
