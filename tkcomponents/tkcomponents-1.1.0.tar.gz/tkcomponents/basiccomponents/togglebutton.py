from tkinter import Button, StringVar

from ..component import Component


class ToggleButton(Component):
    def __init__(self, container, text_values=None, get_data=None, on_change=(lambda button: None),
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        text_values = {} if not text_values else text_values
        self._text_values = {
            True: text_values.get(True, "Hide"),
            False: text_values.get(False, "Show")
        }

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})

        self.is_on = self._get_data(self) if self._get_data else False

        self._text__var = StringVar()
        self._text__var.set(self._text_values[self.is_on])

    def _update(self):
        if self._get_data:
            self.is_on = self._get_data(self)

        self._text__var.set(self._text_values[self.is_on])

    def _render(self):
        self.children["button"] = None

        button = Button(self._frame, textvariable=self._text__var, command=self._handle_click, **self.styles["button"])
        self.children["button"] = button
        button.pack(expand=True, fill="both")

    def _handle_click(self):
        if self._get_data:
            self.is_on = self._get_data(self)

        self.is_on = not self.is_on

        self._on_change(self)

        if self.exists:
            self._update()
