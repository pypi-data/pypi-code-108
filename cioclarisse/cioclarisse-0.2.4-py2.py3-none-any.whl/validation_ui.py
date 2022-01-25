"""
Provide a window in which to display a Validation issues.
"""

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
TITLE_PANEL_HEIGHT = 90


SYMBOL_BUT_WIDTH = 30
CHECKBOX_WIDTH = 50

BOTTOM_BUT_WIDTH = WIDTH // 3


class ValidationWindow(ix.api.GuiWindow):
    """
    The entire window.

    Holds the panel plus buttons to Continue or Cancel.
    """

    def __init__(self, warnings, notices):
        window_height = HEIGHT + BTN_HEIGHT

        super(ValidationWindow, self).__init__(
            ix.application.get_event_window(),
            WINDOW_LEFT,
            WINDOW_TOP,
            WIDTH,
            window_height,
            "Validation",
        )

        self.result = False
        self.warnings =warnings
        self.notices =notices
 
        self.title_widget = ix.api.GuiTextEdit(self, 0, 0, WIDTH, TITLE_PANEL_HEIGHT)
        self.title_widget.set_constraints(C_LEFT, C_TOP, C_RIGHT, C_TOP)
        self.title_widget.set_read_only(True)

        message = ""
        if warnings:
            message += "There are some warnings. Please study them to be sure they don't affect your render.\n\n"
        if notices:
            message += "Please check the notices. The may provide information that affects your render.\n\n"
        message += "You may continue the submission." 

        self.title_widget.set_text(message)
        self.title_widget.set_font_size(14)

        self.text_widget = ix.api.GuiTextEdit(
            self, 0, TITLE_PANEL_HEIGHT, WIDTH, HEIGHT - TITLE_PANEL_HEIGHT
        )
        self.text_widget.set_constraints(C_LEFT, C_TOP, C_RIGHT, C_BOTTOM)

        self.text_widget.set_read_only(True)
        self.close_but = ix.api.GuiPushButton(
            self, 0, HEIGHT, BOTTOM_BUT_WIDTH, BTN_HEIGHT, "Cancel"
        )
        self.close_but.set_constraints(C_LEFT, C_BOTTOM, C_LEFT, C_BOTTOM)
        self.connect(self.close_but, "EVT_ID_PUSH_BUTTON_CLICK", self.on_close_but)


        spacer_width = BOTTOM_BUT_WIDTH

        self.spacer_but = ix.api.GuiPushButton(
            self, BOTTOM_BUT_WIDTH, HEIGHT, spacer_width, BTN_HEIGHT, ""
        )
        self.spacer_but.set_constraints(C_LEFT, C_BOTTOM, C_RIGHT, C_BOTTOM)
        self.spacer_but.set_enable(False)
 
        self.go_but = ix.api.GuiPushButton(
            self,
            (WIDTH - BOTTOM_BUT_WIDTH),
            HEIGHT,
            BOTTOM_BUT_WIDTH,
            BTN_HEIGHT,
            "Continue",
        )
        self.go_but.set_constraints(C_RIGHT, C_BOTTOM, C_RIGHT, C_BOTTOM)

        self.connect(self.go_but, "EVT_ID_PUSH_BUTTON_CLICK", self.on_go_but)

        self._populate()

    def _populate(self):
        """
        Put the missing files in the window.
        """
        warnings = ["[WARN]{}\n".format(w) for w in self.warnings]
        notices = ["[INFO]{}\n".format(n) for n in self.notices]
        
        content = "\n".join(warnings + notices)
        self.text_widget.set_text(content)

    def on_close_but(self, sender, eventid):
        """
        Hide UI so that the event loop exits and window is destroyed.
        """
        self.hide()

    def on_go_but(self, sender, eventid):
        """
        Set result and hide(destroy) the window.
        """
        self.result = True

        self.hide()


def proceed( warnings, notices):
    """
    Show the window  if there are warnings or notices

    Args:
        warnings, notices (list of strings):.

    Returns:
        bool: whether or not the user wants to continue the submission or cancel.
    """
    if not (warnings or notices):
        return True

    win = ValidationWindow( warnings, notices)

    win.show_modal()

    while win.is_shown():
        ix.application.check_for_events()

    return win.result
