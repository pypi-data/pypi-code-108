from objectextensions import Extendable

from abc import ABC
from tkinter import Frame, Widget
from typing import Optional, Any, Callable, Dict


class Component(Extendable, ABC):
    """
    A blank base component which extends lifecycle methods to be overriden as necessary
    """

    def __init__(self, container: Widget,
                 get_data: Optional[Callable[["Component"], Any]] = None, on_change: Callable = lambda: None,
                 update_interval: Optional[int] = None, styles: Optional[Dict[str, dict]] = None):
        super().__init__()

        self._container = container

        self._outer_frame = Frame(self._container)
        self._frame = None  # Add child elements to this frame in ._render()

        # Allow the outer frame to expand to fill the container
        self._outer_frame.rowconfigure(0, weight=1)
        self._outer_frame.columnconfigure(0, weight=1)

        """
        All element styles should be stored here, as their own dicts under a relevant string key.
        self.styles can contain multiple levels of nesting, so that any styles that are passed down to rendered
        child components can then be passed down in turn to the further child components

        Any data supplied in the `styles` param when .__init__() is called must be manually added to self.styles in a
        constructor somewhere in the inheritance chain, otherwise it will be discarded.
        """
        self.styles: Dict[str, dict] = {}

        styles = styles or {}
        self.styles["frame"] = styles.get("frame", {})

        # Use this attribute to store references to any child elements
        self.children = {}

        self._update_interval = update_interval  # Milliseconds

        """
        The below function should receive this component instance as a parameter and return any data from the
        application state that is needed by this component.
        If it is set to None rather than a function, this indicates that there is no outside data source.
        Other aspects of this component (styles, etc.) can be edited during the execution of this function.
        """
        self._get_data = get_data

        """
        When the state of this component changes, the below function should be called and passed this component instance
        and any event data as parameters.
        The function should perform any additional external work needed.
        """
        self._on_change = on_change

    @property
    def exists(self) -> bool:
        """
        Should be used to check that the component has not been destroyed, before its state is altered in any way
        """

        return self._outer_frame.winfo_exists()

    @property
    def is_rendered(self) -> bool:
        """
        Used internally to check that a component has rendered its contained widgets, before checking their details
        """

        if self._frame is None:
            return False

        self._frame.update()
        return self._frame.winfo_exists()

    @property
    def height(self) -> int:
        self._outer_frame.update()
        return self._outer_frame.winfo_height()

    @property
    def width(self) -> int:
        self._outer_frame.update()
        return self._outer_frame.winfo_width()

    @property
    def height_clearance(self) -> Optional[int]:
        """
        Represents the amount of vertical space in the widget (values such as padding and border are removed)
        """

        if not self.is_rendered:
            return None

        frame_padding = self.styles["frame"].get("pady", 0)
        frame_borderwidth = self.styles["frame"].get("borderwidth", 0)
        total_buffer = (2 * frame_padding) + (2 * frame_borderwidth)

        return self._frame.winfo_height() - total_buffer

    @property
    def width_clearance(self) -> Optional[int]:
        """
        Represents the amount of horizontal space in the widget (values such as padding and border are removed)
        """

        if not self.is_rendered:
            return None

        frame_padding = self.styles["frame"].get("padx", 0)
        frame_borderwidth = self.styles["frame"].get("borderwidth", 0)
        total_buffer = (2 * frame_padding) + (2 * frame_borderwidth)

        return self._frame.winfo_width() - total_buffer

    def render(self) -> Frame:
        """
        This method should be invoked externally, and the returned frame have pack() or grid() called on it.
        It will always be called at least once, when setting up/populating the parent widget, but can be
        called again if its child widgets need to be refreshed entirely
        """

        for child_element in self._outer_frame.winfo_children():
            child_element.destroy()
        self._refresh_frame()

        self._render()

        if self._update_interval:
            self._frame.after(self._update_interval, self._update_loop)

        return self._outer_frame

    def update(self) -> None:
        """
        This method should be invoked externally if necessary,
        In situations where ._update() needs to be carried out immediately rather than at the next interval
        """

        if not self.exists:
            return

        self._update()

        if self._needs_render:
            self.render()

    def _update_loop(self) -> None:
        """
        Used internally to handle updating the component once per update interval (if update interval was provided)
        """

        self._frame.after_cancel(self._update_loop)

        if not self.exists:
            return

        if self._update_interval:
            self._frame.after(self._update_interval, self._update_loop)

        self._update()

        if self._needs_render:
            self.render()

    # Overridable Methods

    @property
    def _needs_render(self) -> bool:
        """
        Overridable method.
        Should return a True value only once per time a re-render is required.
        If the component will never need to poll for a re-render, this method need not be overridden
        """

        return False

    def _refresh_frame(self) -> None:
        """
        Overridable method.
        Handles creating a new blank frame to store in self._frame at the top of each render() call.
        Only needs overriding if this blank frame needs extra base functionality
        before any child components are rendered to it
        """

        self._frame = Frame(self._outer_frame, **self.styles["frame"])

        self._frame.grid(row=0, column=0, sticky="nswe")

    def _update(self) -> None:
        """
        Overridable method.
        Handles updating the component state once per update interval (if update interval was provided).
        If the component will not need to directly update its state outside of a new render,
        this method need not be overridden
        """

        pass

    def _render(self) -> None:
        """
        Overridable method.
        Any child components should be rendered to self._frame in this method
        """

        raise NotImplementedError
