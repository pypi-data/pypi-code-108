from tkinter import Label, Button, StringVar
from datetime import datetime, timedelta

from ..component import Component
from ..extensions import GridHelper
from .constants import Constants
from .classes.dateticker import DateTicker


class DateStepper(Component.with_extensions(GridHelper)):
    def __init__(self, container, date_text_format="%Y/%m/%d",
                 get_data=None, on_change=(lambda stepper, increment_amount: None), update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        self.date_text_format = date_text_format

        self._date_ticker = DateTicker()

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["label"] = styles.get("label", {})

        self.offset = self._get_data(self) if self._get_data else 0

        self._date__var = StringVar()
        working_date = datetime.now().date() + timedelta(days=self.offset)
        self._date__var.set(working_date.strftime(self.date_text_format))

    def _update(self):
        if self._date_ticker.is_tomorrow:
            if self.offset != 0:
                self.offset += 1
                self._on_change(self, 1)
            else:
                self._on_change(self, 0)

        if self.exists:
            working_date = datetime.now().date() + timedelta(days=self.offset)
            self._date__var.set(working_date.strftime(self.date_text_format))

            self.children["forward_button"].config(state="disabled" if self.offset == 0 else "normal")

    def _render(self):
        self.children["back_button"] = None
        self.children["forward_button"] = None
        self.children["label"] = None

        self._apply_frame_stretch(rows=[0], columns=[1])

        is_rendering_today = self.offset == 0

        self.children["back_button"] = Button(self._frame, text=Constants.SYMBOLS["arrows"]["left"],
                                              command=lambda: self._handle_click(-1), **self.styles["button"])
        self.children["back_button"].grid(row=0, column=0, sticky="nswe")

        self.children["label"] = Label(self._frame, textvariable=self._date__var, **self.styles["label"])
        self.children["label"].grid(row=0, column=1, sticky="nswe")

        self.children["forward_button"] = Button(self._frame, text=Constants.SYMBOLS["arrows"]["right"],
                                                 command=lambda: self._handle_click(1), **self.styles["button"])
        self.children["forward_button"].grid(row=0, column=2, sticky="nswe")

        self.children["forward_button"].config(state="disabled" if is_rendering_today else "normal")

    def _handle_click(self, increment_amount):
        self.offset += increment_amount

        self.offset = min(self.offset, 0)

        self._on_change(self, increment_amount)

        if self.exists:
            self._update()
