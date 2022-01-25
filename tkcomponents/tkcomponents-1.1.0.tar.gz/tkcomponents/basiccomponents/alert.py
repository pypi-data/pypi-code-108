from tkinter import StringVar, Label, Button

from ..extensions import GridHelper
from ..abstractcomponents.timedframe import TimedFrame
from .constants import Constants


class Alert(TimedFrame.with_extensions(GridHelper)):
    def __init__(self, container, duration, get_data, on_expire=lambda alert: None, update_interval=None, styles=None):
        super().__init__(container, duration, on_expire=on_expire, get_data=get_data,
                         update_interval=update_interval, styles=styles)

        styles = styles or {}
        self.styles["label"] = styles.get("label", {})
        self.styles["button"] = styles.get("button", {})

        self.value = self._get_data(self)

        self._value__var = StringVar()
        self._value__var.set(self.value)

    def _update(self):
        self.value = self._get_data(self)
        self._value__var.set(self.value)

    def _render(self):
        def command__button():
            self.children["progress_bar"].is_expired = True
            self._on_expire(self)

        self.children["label"] = None
        self.children["button"] = None

        self._apply_frame_stretch(columns=[0], rows=[0])

        label = Label(self._frame, textvariable=self._value__var, **self.styles["label"])
        self.children["label"] = label

        button = Button(self._frame, text=Constants.SYMBOLS["cancel"], command=command__button, **self.styles["button"])
        self.children["button"] = button

        label.grid(row=0, column=0, sticky="nswe")
        button.grid(row=0, column=1, sticky="nswe")
