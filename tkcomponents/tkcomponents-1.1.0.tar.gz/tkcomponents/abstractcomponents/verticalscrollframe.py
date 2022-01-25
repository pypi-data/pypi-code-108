from abc import ABC
from tkinter import Frame, Scrollbar, Canvas

from ..component import Component


class VerticalScrollFrame(Component, ABC):
    def __init__(self, container, get_height, get_data=None, on_change=lambda: None,
                 update_interval=None, styles=None):
        super().__init__(container, get_data=get_data, on_change=on_change,
                         update_interval=update_interval, styles=styles)

        """
        To make this frame fit perfectly into a containing Component instance, get_height() should
        return that component's .height_clearance property
        """
        self._get_height = get_height

        styles = styles or {}
        self.styles["inner_frame"] = styles.get("inner_frame", {})
        self.styles["canvas"] = styles.get("canvas", {})
        self.styles["scrollbar"] = styles.get("scrollbar", {})

    def _refresh_frame(self):
        def on_resize(event):
            if not self.is_rendered:
                return

            height = self._get_height()
            width = self._frame.winfo_reqwidth()

            self._frame__canvas.configure(
                width=width,
                height=height,
                scrollregion=self._frame__canvas.bbox("all")
            )
            self._frame.configure(
                width=width,
                height=height
            )

        self._frame__main = Frame(self._outer_frame, **self.styles["frame"])
        self._frame__canvas = Canvas(self._frame__main, highlightthickness=0, **self.styles["canvas"])
        self._frame__scroll = Scrollbar(self._frame__main, orient="vertical", command=self._frame__canvas.yview,
                                        **self.styles["scrollbar"])
        self._frame = Frame(self._frame__canvas, **self.styles["inner_frame"])

        # Custom configuration for the Canvas window
        self._frame__canvas.create_window((0, 0), window=self._frame, anchor="nw")
        self._frame__canvas.configure(
            width=self._frame.winfo_reqwidth(),
            height=self._get_height(),
            scrollregion=self._frame__canvas.bbox("all"),
            yscrollcommand=self._frame__scroll.set)
        self._frame__main.bind("<Configure>", on_resize)
        self._frame__canvas.bind(
            "<MouseWheel>",
            lambda event: self._frame__canvas.yview_scroll(self.__get_scroll_direction(event.delta), "units"))

        self._frame__main.grid(row=0, column=0, sticky="nswe")
        self._frame__scroll.grid(row=0, column=1, sticky="nse")
        self._frame__canvas.grid(row=0, column=0, sticky="nswe")

    def _enable_mousewheel_scroll(self, widget):
        widget.bind(
            "<MouseWheel>",
            lambda event: self._frame__canvas.yview_scroll(self.__get_scroll_direction(event.delta), "units"))

    @staticmethod
    def __get_scroll_direction(event_delta):
        return int(-1 * (event_delta / abs(event_delta)))
