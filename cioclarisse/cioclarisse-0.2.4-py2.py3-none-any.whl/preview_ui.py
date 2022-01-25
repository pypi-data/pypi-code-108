"""Provide a window in which to display a preview submission.

This is required because Clarisse's attribute editor doesn't allow
custom UI to be embedded.
"""

import json
import os

import cioclarisse.utils as cu
import ix

C_LEFT = ix.api.GuiWidget.CONSTRAINT_LEFT
C_TOP = ix.api.GuiWidget.CONSTRAINT_TOP
C_RIGHT = ix.api.GuiWidget.CONSTRAINT_RIGHT
C_BOTTOM = ix.api.GuiWidget.CONSTRAINT_BOTTOM

BTN_HEIGHT = 22
BTN_WIDTH = 100
WINDOW_LEFT = 600
WINDOW_TOP = 200
HEIGHT = 500
WIDTH = 800
PADDING = 5

SYMBOL_BUT_WIDTH = 30
CHECKBOX_WIDTH = 50

BOTTOM_BUT_WIDTH = WIDTH // 3
DOUBLE_BOTTOM_BUT_WIDTH = BOTTOM_BUT_WIDTH*2


def show_submission_responses(response):
    """
    Display submission responese in a window.

    Args:
        response dict: elements contain response codes and descriptsions
    """

    if response.get("status"):
        domain = os.environ.get("CONDUCTOR_AUTH_URL", "https://dashboard.conductortech.com")
        url = "{}{}".format(domain,str(response["uri"].replace("jobs", "job")))

        ix.application.message_box(
            url,
            "Conductor Submission: Info",
            ix.api.AppDialog.yes(),
            ix.api.AppDialog.STYLE_OK,
        )
        return
    msg = "Submission failed"
    ix.application.message_box(
        msg,
        "Conductor Submission: Info",
        ix.api.AppDialog.yes(),
        ix.api.AppDialog.STYLE_OK,
        )


class PreviewWindow(ix.api.GuiWindow):
    """The entire window.

    Holds the panel plus buttons to Submit or Cancel.
    """

    def __init__(self, submission):
        window_height = HEIGHT + BTN_HEIGHT

        super(PreviewWindow, self).__init__(
            ix.application.get_event_window(),
            WINDOW_LEFT,
            WINDOW_TOP,
            WIDTH,
            window_height,
            "Submission Preview",
        )

        self.submission = submission
        self.text_widget = ix.api.GuiTextEdit(self, 0, 0, WIDTH, HEIGHT)
        self.text_widget.set_constraints(C_LEFT, C_TOP, C_RIGHT, C_BOTTOM)
        self.text_widget.set_read_only(True)
        self.close_but = ix.api.GuiPushButton(
            self, 0, HEIGHT, BOTTOM_BUT_WIDTH, BTN_HEIGHT, "Close"
        )
        self.close_but.set_constraints(C_LEFT, C_BOTTOM, C_LEFT, C_BOTTOM)
        self.connect(self.close_but, "EVT_ID_PUSH_BUTTON_CLICK", self.on_close_but)

        self.spacer_but = ix.api.GuiPushButton(
            self, BOTTOM_BUT_WIDTH, HEIGHT, DOUBLE_BOTTOM_BUT_WIDTH, BTN_HEIGHT, ""
        )
        self.spacer_but.set_constraints(C_LEFT, C_BOTTOM, C_RIGHT, C_BOTTOM)
        self.spacer_but.set_enable(False)

        self._populate()

    def _populate(self):
        """
        Put the submission args in the window.
        """
        submission_args = self.submission.get_args()
        json_jobs = json.dumps(submission_args, indent=3, sort_keys=True)
        self.text_widget.set_text(json_jobs)

    def on_close_but(self, sender, eventid):
        """
        Hide UI so that the event loop exits and window is destroyed.
        """
        self.hide()
 


def build(submission, **kw):
    """
    Show and populate the preview window.

    Populate it with submission args for each job.

    Args:
        submission (Submission): Submission object
    """
    win = PreviewWindow(submission)

    win.show_modal()
    while win.is_shown():
        ix.application.check_for_events()
