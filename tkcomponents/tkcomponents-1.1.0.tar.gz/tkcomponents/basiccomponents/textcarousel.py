from tkinter import Label, Button, StringVar

from ..component import Component
from ..extensions import GridHelper
from .constants import Constants


class TextCarousel(Component.with_extensions(GridHelper)):
    def __init__(self, container,
                 get_data, on_change=(lambda carousel, increment_amount: None),
                 amount_to_display=1, index=0, update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        self.index = index

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["label"] = styles.get("label", {})

        self.values = self._get_data(self)

        self._displayed_text__vars = [StringVar() for i in range(amount_to_display)]
        self._update_displayed_text()

    def _update(self):
        self.values = self._get_data(self)

        self._update_displayed_text()

        self._set_button_states()

    def _render(self):
        self.children["back_button"] = None
        self.children["forward_button"] = None
        self.children["labels"] = []

        row_index, column_index = 0, 0

        self._apply_frame_stretch(columns=list(range(1, len(self._displayed_text__vars)+1)), rows=[0])

        back_button = Button(self._frame, text=Constants.SYMBOLS["arrows"]["left"],
                             command=lambda: self._handle_click(-1), **self.styles["button"])
        self.children["back_button"] = back_button
        back_button.grid(row=row_index, column=column_index, sticky="nswe")
        column_index += 1

        for text__var in self._displayed_text__vars:
            label = Label(self._frame, textvariable=text__var, **self.styles["label"])
            self.children["labels"].append(label)
            label.grid(row=row_index, column=column_index, sticky="nswe")
            column_index += 1

        forward_button = Button(self._frame, text=Constants.SYMBOLS["arrows"]["right"],
                                command=lambda: self._handle_click(1), **self.styles["button"])
        self.children["forward_button"] = forward_button
        forward_button.grid(row=row_index, column=column_index, sticky="nswe")

        self._set_button_states()

    def _handle_click(self, increment_amount):
        self.values = self._get_data(self)

        self.index += increment_amount
        self.index = max(0, self.index)
        self.index = min(len(self.values) - len(self._displayed_text__vars), self.index)

        self._on_change(self, increment_amount)

        if self.exists:
            self._update()

    def _set_button_states(self):
        self.children["back_button"].config(state="disabled" if self.index == 0 else "normal")
        self.children["forward_button"].config(
            state="disabled" if self.index + len(self._displayed_text__vars) == len(self.values) else "normal")

    def _update_displayed_text(self):
        for var_index, text__var in enumerate(self._displayed_text__vars):
            value = self.values[self.index + var_index]
            text__var.set(value)
