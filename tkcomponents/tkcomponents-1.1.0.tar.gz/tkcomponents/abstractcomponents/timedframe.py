from abc import ABC
from tkinter import Frame
from datetime import datetime

from ..component import Component
from ..basiccomponents.progressbar import ProgressBar


class TimedFrame(Component, ABC):
    def __init__(self, container, duration, on_expire=lambda timed_frame: None, get_data=None, on_change=lambda: None,
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        self.started = datetime.now()
        self.duration = duration  # Provide in milliseconds, as with update_interval

        self._on_expire = on_expire

        styles = styles or {}
        self.styles["progress_bar"] = styles.get("progress_bar", {})
        self.styles["inner_frame"] = styles.get("inner_frame", {})

    def _refresh_frame(self):
        def get_data__progress_bar(bar):
            elapsed = datetime.now() - self.started
            elapsed_proportion = min(1, (elapsed.total_seconds() * 1000) / self.duration)
            return elapsed_proportion

        self.children["progress_bar"] = None

        self._frame__main = Frame(self._outer_frame, **self.styles["frame"])

        self.children["progress_bar"] = ProgressBar(
            self._frame__main,
            get_data=get_data__progress_bar,
            on_change=lambda bar: self._on_expire(self),
            is_reversed=True,
            styles={
                "height": 3,
                **self.styles["progress_bar"]
            }
        )
        progress_bar_frame = self.children["progress_bar"].render()
        self._frame = Frame(self._frame__main, **self.styles["inner_frame"])

        self._frame__main.rowconfigure(0, weight=1)
        self._frame__main.columnconfigure(0, weight=1)
        self._frame.bind(
            "<Configure>",
            lambda event: progress_bar_frame.configure(width=self._frame.winfo_reqwidth())
        )

        self._frame__main.grid(row=0, column=0, sticky="nswe")
        progress_bar_frame.grid(row=1, column=0, sticky="nswe")
        self._frame.grid(row=0, column=0, sticky="nswe")
