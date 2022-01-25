from tkinter import Label, StringVar

from ..component import Component


class LabelWrapper(Component):
    def __init__(self, container, get_data,
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data,
                         update_interval=update_interval, styles=styles)

        styles = styles or {}
        self.styles["label"] = styles.get("label", {})

        self._text__var = StringVar()
        self._text__var.set(self._get_data(self))

    def _update(self):
        self._text__var.set(self._get_data(self))

    def _render(self):
        self.children["label"] = None

        label = Label(self._frame, textvariable=self._text__var, **self.styles["label"])
        self.children["label"] = label
        label.pack(expand=True, fill="both")
