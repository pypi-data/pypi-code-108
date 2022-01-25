from tkinter import Entry, StringVar

from ..component import Component
from ..extensions import GridHelper


class StringEditor(Component.with_extensions(GridHelper)):
    def __init__(self, container, get_data=None, on_change=(lambda editor, old_value: None),
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        styles = styles or {}
        self.styles["entry"] = styles.get("entry", {})
        self.styles["entry_saved"] = styles.get("entry_saved", {})
        self.styles["entry_unsaved"] = styles.get("entry_unsaved", {})

        self.__entry_style__current = None  # Used by __apply_entry_style

        self.value = self._get_data(self) if self._get_data else ""

        self._value__var = StringVar()
        self._value__var.set(self.value)
        self._value__var.trace_add("write", lambda *args: self._handle_input())

    @property
    def is_unsaved(self):
        if not self._get_data:
            return False

        source_value = self._get_data(self)
        return source_value != self.value

    def _update(self):
        self.__apply_entry_style("entry_unsaved" if self.is_unsaved else "entry_saved")

    def _render(self):
        self.children["entry"] = None

        self._apply_frame_stretch(columns=[0], rows=[0])

        # Registering validation callbacks
        for command_option in ("validatecommand", "invalidcommand"):
            if command_option in self.styles["entry"]:
                option_data = self.styles["entry"][command_option]
                if callable(option_data):
                    self.styles["entry"][command_option] = self._frame.register(option_data)
                else:
                    self.styles["entry"][command_option] = (
                        self._frame.register(option_data[0]),
                        *option_data[1:]
                    )

        entry = Entry(self._frame, textvariable=self._value__var, **self.styles["entry"])
        self.children["entry"] = entry
        entry.grid(row=0, column=0, sticky="nswe")

        self.__apply_entry_style("entry_saved")

    def _handle_input(self):
        old_value = self.value
        self.value = self._value__var.get()

        self._on_change(self, old_value)

        if self.exists:
            self._update()

    def __apply_entry_style(self, style_key):
        """
        This method exists to minimise calls to .configure(), as they can impact insertion cursor functionality
        """

        if style_key != self.__entry_style__current:
            self.__entry_style__current = style_key
            self.children["entry"].configure(**self.styles[style_key])
