from functools import partial
from tkinter import Label

from ..component import Component
from ..extensions import GridHelper
from .numberstepper import NumberStepper


class NumberStepperTable(Component.with_extensions(GridHelper)):
    def __init__(self, container, axis_labels, axis_values,
                 get_data=None, on_change=(lambda x_value, y_value, stepper, increment_amount: None),
                 text_format="{0}", step_amounts=(1,), limits=(None, None), is_horizontal=True,
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change, styles=styles)

        self._stepper_kwargs = {
            "text_format": text_format,
            "step_amounts": step_amounts,
            "limits": limits,
            "update_interval": update_interval,
            "is_horizontal": is_horizontal,
            "styles": styles.get("number_stepper", {})
        }

        self.axis_labels = axis_labels
        self.axis_values = axis_values

        styles = styles or {}
        self.styles["x_label"] = styles.get("x_label", {})
        self.styles["y_label"] = styles.get("y_label", {})

    def _render(self):
        self.children["axis_labels"] = [[], []]
        self.children["number_steppers"] = {}

        self._apply_frame_stretch(columns=[0], rows=[1])

        for x_index, x_label in enumerate(self.axis_labels[0]):
            label = Label(self._frame, text=x_label, **self.styles["x_label"])
            self.children["axis_labels"][0].append(label)
            label.grid(row=0, column=x_index+1, sticky="nswe")

        for y_index, y_label in enumerate(self.axis_labels[1]):
            label = Label(self._frame, text=y_label, **self.styles["y_label"])
            self.children["axis_labels"][1].append(label)
            label.grid(row=y_index+2, column=0, sticky="nswe")

        for x_index, x_value in enumerate(self.axis_values[0]):
            for y_index, y_value in enumerate(self.axis_values[1]):
                number_stepper = NumberStepper(
                    self._frame,
                    get_data=partial(self._get_data, x_value, y_value) if self._get_data else None,
                    on_change=partial(self._on_change, x_value, y_value),
                    **self._stepper_kwargs
                )
                self.children["number_steppers"][(x_index, y_index)] = number_stepper
                number_stepper.render().grid(row=y_index+2, column=x_index+1, sticky="nswe")
