"""
Handle the submission.
"""

from contextlib import contextmanager
 
import time
from PySide2 import QtWidgets 
import threading
import nuke
from ciocore import conductor_submit
import traceback
from ciocore import config
import json
from cionuke import const as k



try:
    import urlparse as parse
except ImportError:
    from urllib import parse

from cionuke import validation

from cionuke.widgets.buttoned_scroll_dialog import ButtonedScrollDialog
from cionuke.widgets.notice_grp import NoticeGrp

from cionuke.components import (
    project,
    title,
    instance_type,
    software,
    environment,
    metadata,
    assets,
    frames,
    advanced,
)

# NOTE: The order is important!
# assets comes first because dependency scraping might be expensive.
# We need the results of dependency scraping in order to form the
# windows path mapping args, which are used by the frames component,
# where tasks are generated.
COMPONENTS = (
    assets,
    project,
    title,
    instance_type,
    software,
    environment,
    metadata,
    frames,
    advanced,
)


HEADER_ERROR = [
    "There are issues that would cause your submission to fail.",
    "To save you unwanted costs, the submission is blocked. ",
    "Please attend to the errors listed below and try again.",
]

HEADER_WARNING = [
    "There are issues that could cause unexpected results in your render.",
    "Please read the messages carefully.",
    "If everything looks okay, you can continue with the submission.",
]

HEADER_INFO = [
    "There are some informational notices below.",
    "Please read the messages.",
    "If everything looks okay, continue with the submission.",
]


@contextmanager
def create_directories_on(submitter):
    """
    Turn on create_directoiries on write nodes for the submission.
    """
    write_nodes = [n for n in submitter.dependencies() if n.Class() == "Write"]
    orig_states = [w.knob("create_directories").value() for w in write_nodes]
    zipped = zip(write_nodes, orig_states)
    try:
        for pair in zipped:
            pair[0].knob("create_directories").setValue(1)
        yield
    finally:
        for pair in zipped:
            pair[0].knob("create_directories").setValue(pair[1])


@contextmanager
def transient_save(submitter):
    """
    Save with the autosave name for submission, then revert.
    """
    cio_filename = submitter.knob("cio_autosave_template").getValue()
    try:
        original = nuke.Root().knob("name").getValue()
        nuke.scriptSaveAs(cio_filename, overwrite=1)
        yield
    except OSError:
        print("Problem saving nuke script")
    finally:
        nuke.Root().knob("name").setValue(original)


class SubmissionDialog(ButtonedScrollDialog):
    def __init__(self, submitter, submitting, messages):
        self.submitting = submitting
        title = "Submission" if submitting else "Validation"
        super(SubmissionDialog, self).__init__(
            submitter, title=title, buttons=[("cancel", "Close"), ("continue", "Continue")]
        )

        self.resize(600 * self.screen_scale, 800 * self.screen_scale)
        self.buttons["cancel"].clicked.connect(self.reject)
        self.populate_validation_messages(messages)

    def populate_validation_messages(self, messages):

        widgets = []
        for severity in ["error", "warning", "info"]:
            for entry in messages[severity]:
                widgets.append(NoticeGrp(entry, severity))
        header_msg = None
        if messages["error"]:
            if self.submitting:
                header_msg = "\n".join(HEADER_ERROR)
            else:
                header_msg = HEADER_ERROR[0]
        elif messages["warning"]:
            if self.submitting:
                header_msg = "\n".join(HEADER_WARNING)
            else:
                header_msg = HEADER_WARNING[0]
        elif messages["info"]:
            if self.submitting:
                header_msg = "\n".join(HEADER_INFO)
            else:
                header_msg = HEADER_INFO[0]
        else:
            msg = "We found no issues with this submission."
            if self.submitting:
                msg += " Please continue."
            widgets.append(NoticeGrp(msg, "success"))

        if header_msg:
            header_widget = QtWidgets.QLabel()
            header_widget.setWordWrap(True)
            header_widget.setText(header_msg)
            widgets = [header_widget] + widgets

        self.populate(widgets)
        if self.submitting and not messages["error"]:
            self.buttons["continue"].setVisible(True)
            self.buttons["continue"].clicked.connect(self.continue_submission)
        else:
            self.buttons["continue"].setVisible(False)

    def continue_submission(self):

        try:
            response, response_code = self.save_and_submit()
        except BaseException as ex:
            response = {"body": str(ex)}
        if not response:
            response = {"body": "Submission cancelled."}
        self.handle_response(response)

    def save_and_submit(self):
        """
        Save or autosave, then submit

        Returns:
            tuple: submission response and code.
        """

        do_autosave = bool(self.submitter.knob("cio_do_autosave").getValue())
        if do_autosave:
            with transient_save(self.submitter):
                with create_directories_on(self.submitter):
                    return self.do_submission()
        else:
            with create_directories_on(self.submitter):
                if nuke.Root().modified():
                    if not nuke.scriptSave():
                        return (False, False)
                return self.do_submission()

    def do_submission(self):
        """
        Do submission.

        Returns:
            tuple: submission response.
        """

        kwargs = {"should_scrape_assets": True}
        submission = resolve_submission(self.submitter, **kwargs)
        remote_job = conductor_submit.Submit(submission)
        return remote_job.main()

    def handle_response(self, response):

        if response.get("status") == "success":
            try:
                success_widget = self.get_success_widget(response)
                info_widget = self.get_downloader_info_widget(response)
                daemon_widget = self.get_daemon_widget()
                widgets = list(filter(None, [success_widget, info_widget, daemon_widget]))
            except BaseException as ex:
                widgets = [NoticeGrp(str(ex), "error")]
        else:
            widgets = [NoticeGrp(response["body"], "error")]

        self.clear()
        self.populate(widgets)
        self.buttons["continue"].setVisible(False)

    def get_success_widget(self,response):
        cfg = config.config().config
        success_uri = response["uri"].replace("jobs", "job")
        url = parse.urljoin(cfg["url"], success_uri)
        message = "Success!\nClick to go to the Dashboard.\n{}".format(url)
        return NoticeGrp(message, "success", url)

    def get_downloader_info_widget(self,response):
        job_id = response["uri"].split("/")[-1]
        dl_command = "\"{}\" downloader --job_id {}".format(k.CONDUCTOR_COMMAND_PATH, job_id)
        info = "To download finished frames, either use the Companion app, or enter the following command in a terminal or command prompt:\n '{}'".format(
            dl_command
        )
        return NoticeGrp(info, "info")

    def get_daemon_widget(self):
        use_daemon = self.submitter.knob("cio_use_daemon").getValue()
        if not use_daemon:
            return
        location = self.submitter.knob("cio_location").getValue().strip()
        if location:
            msg = "This submission expects an uploader daemon to be running and set to a specific location tag.\n"
            msg += "If you haven't already done so, open a shell and type:\n\'{}' uploader --location {}\n\n".format(
                k.CONDUCTOR_COMMAND_PATH, location
            )
        else:
            msg = "This submission expects an uploader daemon to be running.\n"
            msg += "If you haven't already done so, open a shell and type:\n'{}' uploader\n\n".format(
                k.CONDUCTOR_COMMAND_PATH
            )
        print(msg)
        msg += "You'll also find this information in the script editor.\n"

        return NoticeGrp(msg, "info")


def submit(submitter, submitting):
    """
    Submit and handle the response

    This is the entry for this module.
    """

    messages = validation.run(submitter)
    dialog = SubmissionDialog(submitter, submitting, messages)
    result = dialog.exec_()

    return bool(result)


def resolve_submission(submitter, **kwargs):
    """
    Compile submission payload from all components.

    Returns:
        dict: payload, including tasks, assets, project, and so on
    """
    submission = {}

    for component in COMPONENTS:
        submission.update(component.resolve(submitter, **kwargs))
    return submission
