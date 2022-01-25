from tkinter import Frame

from ..component import Component
from ..extensions import GridHelper


class ProgressBar(Component.with_extensions(GridHelper)):
    RESOLUTION = 10000

    def __init__(self, container, get_data, on_change=lambda bar: None, is_reversed=False,
                 update_interval=15, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        self.is_reversed = is_reversed
        self.is_expired = False

        styles = styles or {}
        self.styles["filled_bar_frame"] = styles.get("filled_bar_frame", {})
        self.styles["empty_bar_frame"] = styles.get("empty_bar_frame", {})
        self.styles["width"] = styles.get("width", None)
        self.styles["height"] = styles.get("height", None)

        self.value = self._get_data(self)  # Should return proportion elapsed as a decimal between 0 and 1

    def _update(self):
        old_value = self.value
        self.value = self._get_data(self)

        if (old_value in (0, 1)) != (self.value in (0, 1)) or abs(self.value - old_value) == 1:
            if self.value == 1:
                if not self.is_expired:
                    self.is_expired = True
                    self._on_change(self)
            if self.exists:
                self.render()
        else:
            self._configure_bar_proportions()

    def _render(self):
        self.children["filled_bar_frame"] = None
        self.children["empty_bar_frame"] = None

        self._apply_frame_stretch(rows=[0])

        if self.value in (0, 1):
            bar_style = "empty_bar_frame" if self.value == self.is_reversed else "filled_bar_frame"

            bar_frame = Frame(self._frame, **self.styles[bar_style])
            self.children[bar_style] = bar_frame
            bar_frame.grid(row=0, column=0, sticky="nswe")

        else:
            filled_bar_frame = Frame(self._frame, **self.styles["filled_bar_frame"])
            self.children["filled_bar_frame"] = filled_bar_frame
            filled_bar_frame.grid(row=0, column=0, sticky="nswe")

            empty_bar_frame = Frame(self._frame, **self.styles["empty_bar_frame"])
            self.children["empty_bar_frame"] = empty_bar_frame
            empty_bar_frame.grid(row=0, column=1, sticky="nswe")

        self._configure_bar_proportions()

    def _configure_bar_proportions(self):
        if self.value in (0, 1):
            self._frame.columnconfigure(0, weight=1)

            if self.styles["width"]:
                self._frame.columnconfigure(0, minsize=self.styles["width"])

        else:
            resolution = self.styles["width"] or self.RESOLUTION

            completed_width = int(self.value*resolution)  # Always floor how complete the bar is
            if self.is_reversed:
                empty_width = completed_width
                filled_width = resolution - completed_width
            else:
                filled_width = completed_width
                empty_width = resolution - completed_width

            self._frame.columnconfigure(0, weight=filled_width)
            self._frame.columnconfigure(1, weight=empty_width)

            if self.styles["width"]:
                self._frame.columnconfigure(0, minsize=filled_width)
                self._frame.columnconfigure(1, minsize=empty_width)

        if self.styles["height"]:
            self._frame.rowconfigure(0, minsize=self.styles["height"])
