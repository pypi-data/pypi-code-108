from tkinter import Button
from functools import partial

from ..abstractcomponents.verticalscrollframe import VerticalScrollFrame


class ButtonListBox(VerticalScrollFrame):
    def __init__(self, container, current_value, get_height,
                 get_data, on_change=(lambda picker, new_value: None), styles=None):
        super().__init__(container, get_height,
                         get_data=get_data, on_change=on_change, styles=styles)

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["button_selected"] = styles.get("button_selected", {})

        self.values = {}
        self.order = []

        for data_obj in self._get_data(self):
            self.order.append(data_obj["value"])
            self.values.update({
                data_obj["value"]: {"text": data_obj["text"], "style": data_obj.get("style", {})}
            })  # Individual button styles are optional, and so do not have to be passed in by get_data

        if current_value not in self.values:
            raise ValueError
        self.current_value = current_value

    def _update(self):
        self._set_button_states()

    def _render(self):
        self.children["buttons"] = {}

        row_index = 0
        for value in self.order:
            row_index += 1
            data = self.values[value]
            button = Button(self._frame, text=data["text"], command=partial(self._handle_click, value),
                            **{**self.styles["button"], **data["style"]})
            self._enable_mousewheel_scroll(button)
            self.children["buttons"][value] = button
            button.grid(row=row_index, column=0, sticky="nswe")

        self._set_button_states()

    def _handle_click(self, new_value):
        self.current_value = new_value

        self._on_change(self, new_value)

        if self.exists:
            self._update()

    def _set_button_states(self):
        for value, button in self.children["buttons"].items():
            if value == self.current_value:
                button.configure(state="disabled", **self.styles["button_selected"])
            else:
                button.configure(state="normal", **{**self.styles["button"], **self.values[value]["style"]})
