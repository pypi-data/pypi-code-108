from tkinter import Label, Button, StringVar

from ..component import Component
from ..extensions import GridHelper
from .classes.timer import Timer


class TimerControl(Component.with_extensions(GridHelper)):
    def __init__(self, container, get_data=None, on_change=(lambda timer_control, method_key: None),
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["label"] = styles.get("label", {})

        self.timer = self._get_data(self) if self._get_data else Timer()

        self._time_elapsed__var = StringVar()
        self._toggle_button__var = StringVar()

        self._time_elapsed__var.set(self.timer.elapsed_string)
        self._toggle_button__var.set("Stop" if self.timer.is_running else "Start")

    def _update(self):
        self._time_elapsed__var.set(self.timer.elapsed_string)
        self._toggle_button__var.set("Stop" if self.timer.is_running else "Start")

    def _render(self):
        self.children["toggle_button"] = None
        self.children["reset_button"] = None
        self.children["label"] = None

        self._apply_frame_stretch(rows=[0], columns=[1])

        row_index, column_index = 0, 0

        toggle_button = Button(self._frame, textvariable=self._toggle_button__var,
                               command=lambda: self._handle_click("toggle"), **self.styles["button"])
        self.children["toggle_button"] = toggle_button
        toggle_button.grid(row=row_index, column=column_index, sticky="nswe")
        column_index += 1

        label = Label(self._frame, textvariable=self._time_elapsed__var, **self.styles["label"])
        self.children["label"] = label
        label.grid(row=row_index, column=column_index, sticky="nswe")
        column_index += 1

        reset_button = Button(self._frame, text="Reset", command=lambda: self._handle_click("reset"),
                              **self.styles["button"])
        self.children["reset_button"] = reset_button
        reset_button.grid(row=row_index, column=column_index, sticky="nswe")

    def _handle_click(self, method_key):
        if method_key == "toggle":
            if self.timer.is_running:
                self.timer.stop()
            else:
                self.timer.start()
        elif method_key == "reset":
            self.timer.reset()
        else:
            raise ValueError

        self._on_change(self, method_key)

        if self.exists:
            self._update()
