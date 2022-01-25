from tkinter import Label, Button, StringVar
from functools import partial

from ..component import Component
from ..extensions import GridHelper


class NumberStepper(Component.with_extensions(GridHelper)):
    def __init__(self, container, get_data=None, on_change=(lambda stepper, increment_amount: None),
                 text_format="{0}", step_amounts=(1,), limits=(None, None), is_horizontal=True,
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        self.text_format = text_format

        self.min = limits[0]
        self.max = limits[1]

        self.is_horizontal = is_horizontal
        self.step_amounts = step_amounts  # Provide only positive values, they will be mirrored for negative values

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["label"] = styles.get("label", {})

        self.value = self._get_data(self) if self._get_data else 0

        self._value__var = StringVar()
        self._value__var.set(self.text_format.format(self.value))

    def _update(self):
        if self._get_data:
            self.value = self._get_data(self)

        self._value__var.set(self.text_format.format(self.value))

        self._set_button_states()

    def _render(self):
        self.children["minus_buttons"] = []
        self.children["plus_buttons"] = []
        self.children["label"] = None

        row_stretch = [0] if self.is_horizontal else [len(self.step_amounts)]
        column_stretch = [len(self.step_amounts)] if self.is_horizontal else [0]
        self._apply_frame_stretch(rows=row_stretch, columns=column_stretch)

        row_index, column_index = 0, 0

        if self.is_horizontal:
            for step_amount in reversed(self.step_amounts):
                button = Button(self._frame, text="-{0}".format("" if step_amount == 1 else step_amount),
                                command=partial(self._handle_click, -step_amount), **self.styles["button"])
                self.children["minus_buttons"].append(button)
                button.grid(row=row_index, column=column_index, sticky="nswe")
                column_index += 1

            self.children["label"] = Label(self._frame, textvariable=self._value__var, **self.styles["label"])
            self.children["label"].grid(row=row_index, column=column_index, sticky="nswe")
            column_index += 1

            for step_amount in self.step_amounts:
                button = Button(self._frame, text="+{0}".format("" if step_amount == 1 else step_amount),
                                command=partial(self._handle_click, step_amount), **self.styles["button"])
                self.children["plus_buttons"].append(button)
                button.grid(row=row_index, column=column_index, sticky="nswe")
                column_index += 1

        else:
            for step_amount in reversed(self.step_amounts):
                button = Button(self._frame, text="+{0}".format("" if step_amount == 1 else step_amount),
                                command=partial(self._handle_click, step_amount), **self.styles["button"])
                self.children["plus_buttons"].append(button)
                button.grid(row=row_index, column=column_index, sticky="nswe")
                row_index += 1

            self.children["label"] = Label(self._frame, textvariable=self._value__var, **self.styles["label"])
            self.children["label"].grid(row=row_index, column=column_index, sticky="nswe")
            row_index += 1

            for step_amount in self.step_amounts:
                button = Button(self._frame, text="-{0}".format("" if step_amount == 1 else step_amount),
                                command=partial(self._handle_click, -step_amount), **self.styles["button"])
                self.children["minus_buttons"].append(button)
                button.grid(row=row_index, column=column_index, sticky="nswe")
                row_index += 1

        self._set_button_states()

    def _handle_click(self, increment_amount):
        if self._get_data:
            self.value = self._get_data(self)

        self.value += increment_amount
        if self.min is not None:
            self.value = max(self.min, self.value)
        if self.max is not None:
            self.value = min(self.max, self.value)

        self._on_change(self, increment_amount)

        if self.exists:
            self._update()

    def _set_button_states(self):
        for button in self.children["minus_buttons"]:
            button.config(state="disabled" if self.value == self.min else "normal")

        for button in self.children["plus_buttons"]:
            button.config(state="disabled" if self.value == self.max else "normal")
