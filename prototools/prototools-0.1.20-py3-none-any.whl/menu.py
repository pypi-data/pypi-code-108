import os
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Tuple

from prototools.components import (
    Dimension,
    Footer,
    Header,
    Items,
    Prompt,
    Screen,
    Style,
    Text,
)
from prototools.config import HEIGHT, WIDTH
from prototools.keyboard import Keyboard, arrow_position
from prototools.utils import strip_ansi

try:
    import msvcrt
except ImportError:
    pass


def get_option_win(options: Sequence, menu) -> int:
    """Gets the menu item by using arrow keys.

    Args:
        options (Sequence): Sequence of menu items
        menu (Menu): Menu
    
    Returns:
        int: Position of the menu item.
    """
    from prototools.keyboard import getch
    #width = menu.builder._items._calculate_content_width()
    width = menu.builder._max_dimension.width # TODO: Fix this
    pad = (menu.builder._header.style.padding.left * 2)
    event = ""
    position = 0
    print(str(options[position]), end="\r")
    while True:
        extra = len(strip_ansi(str(options[position])))
        print(" " + str(options[position]) + " "*((width-extra-pad-1)), end="\r")
        k = ord(getch())
        if k in (Keyboard.ESC, Keyboard.ENTER):
            break
        elif k in Keyboard.SPECIAL_KEYS:
            k = getch()
            event = Keyboard.action(k)
        position = arrow_position(position, len(options), event)
    return position


def get_option_posix(options: Sequence, menu) -> int:
    """Gets the menu item by using arrow keys.

    Args:
        options (Sequence): Sequence of menu items
        menu (Menu): Menu
    
    Returns:
        int: Position of the menu item.
    """
    from prototools.keyboard import getch
    #width = menu.builder._items._calculate_content_width()
    width = menu.builder._max_dimension.width # TODO: Fix this
    pad = (menu.builder._header.style.padding.left * 2)
    event = ""
    position = 0
    print(str(options[position]), end="\r")
    while True:
        extra = len(strip_ansi(str(options[position])))
        print(" " + str(options[position]) + " "*((width-extra-pad-1)), end="\r")
        k = getch()
        if k == "j" or k == "k":
            event = k
        elif k == "\r":
            break
        position = arrow_position(position, len(options), event)
    return position


if os.name == "nt":
    get_option = get_option_win
else:
    get_option = get_option_posix


class Builder:
    """Builder class for generating the menu.
    """
    
    def __init__(
        self, 
        max_dimension: Optional[Dimension] = None,
    ) -> None:
        if max_dimension is None:
            max_dimension = Dimension(width=WIDTH, height=HEIGHT)
        self._max_dimension = max_dimension
        self._border_style = "light"
        self._header = Header(Style(), max_dimension)
        self._prologue = Text(Style(), max_dimension)
        self._items = Items(Style(), max_dimension)
        self._epilogue = Text(Style(), max_dimension)
        self._footer = Footer(Style(), max_dimension)
        self._prompt = Prompt(Style(), max_dimension)

    @property
    def style(self) -> Style:
        """Style property."""
        return self._style

    @property
    def header(self) -> Header:
        """Header property."""
        return self._header

    @property
    def prologue(self) -> Text:
        """Prologue property."""
        return self._prologue

    @property
    def epilogue(self) -> Text:
        """Epilogue property."""
        return self._epilogue

    @property
    def footer(self) -> Footer:
        """Footer property."""
        return self._footer

    # =========================================================================
    # Style and Dimension Settings
    # =========================================================================

    def set_dimension(self, width: int, height: int) -> None:
        """Set the dimension of the menu."""
        self._max_dimension.width = width
        self._max_dimension.height = height
        return self

    def set_style(self, border_style: str):
        """Set the border style."""
        if border_style not in (
            "ascii", "light", "heavy", "double", "borderless"
        ):
            raise ValueError(
                "'border_style' must be" \
                " ascii, light, heavy, double or borderless"
            )
        self._header.style.border.set_style(border_style)
        self._prologue.style.border.set_style(border_style)
        self._items.style.border.set_style(border_style)
        self._epilogue.style.border.set_style(border_style)
        self._footer.style.border.set_style(border_style)
        self._prompt.style.border.set_style(border_style)
        return self
    
    # =========================================================================
    # Margins, Paddings ans Misc. Settings (affects all components)
    # =========================================================================

    def set_margins(self, margin: Tuple[int, int, int, int]):
        """Set the margins."""
        left, right, top, bottom = margin

        self._header.style.margin.top = top
        self._header.style.margin.left = left
        self._header.style.margin.right = right
        self._prologue.style.margin.left = left
        self._prologue.style.margin.right = right
        self._items.style.margin.left = left
        self._items.style.margin.right = right
        self._epilogue.style.margin.left = left
        self._epilogue.style.margin.right = right
        self._footer.style.margin.left = left
        self._footer.style.margin.right = right
        self._footer.style.margin.bottom = bottom
        return self
    
    def set_paddings(self, padding: Tuple[int, int, int, int]):
        """Set the paddings."""
        left, right, top, bottom = padding

        self._header.style.padding.left = left
        self._header.style.padding.right = right
        self._header.style.padding.top = top
        self._header.style.padding.bottom = bottom
        self._prologue.style.padding.left = left
        self._prologue.style.padding.right = right
        self._prologue.style.padding.top = top
        self._prologue.style.padding.bottom = bottom
        self._items.style.padding.left = left
        self._items.style.padding.right = right
        self._items.style.padding.top = top
        self._items.style.padding.bottom = bottom
        self._epilogue.style.padding.left = left
        self._epilogue.style.padding.right = right
        self._epilogue.style.padding.top = top
        self._epilogue.style.padding.bottom = bottom
        self._footer.style.padding.left = left
        self._footer.style.padding.right = right
        self._footer.style.padding.top = top
        self._footer.style.padding.bottom = bottom
        return self

    def set_separators(self, flag: bool):
        """Set the separators."""
        self.show_header_bottom(flag)
        self.show_prologue_bottom(flag)
        self.show_epilogue_top(flag)
        return self

    def set_color(self, color: Callable):
        self._header._color = color
        self._prologue._color = color
        self._items._color = color
        self._epilogue._color = color
        self._footer._color = color
        self._prompt._color = color

    # ========================================================================
    # Header Settings
    # ========================================================================

    def set_title_align(self, align="center"):
        """Set the title align."""
        if align not in ("left", "center", "right"):
            raise ValueError(
                "'align' must be left, center or right"
            )
        self._header.title_align = align
        return self

    def set_subtitle_align(self, align: str):
        """Set the alignment of the subtitle."""
        if align not in ("left", "center", "right"):
            raise ValueError(
                "'align' must be left, center or right"
            )
        self._header.subtitle_align = align
        return self

    def set_header_paddings(self, padding: Tuple[int, int, int, int]):
        """Set the paddings of the header."""
        left, right, top, bottom = padding

        self._header.style.padding.left = left
        self._header.style.padding.right = right
        self._header.style.padding.top = top
        self._header.style.padding.bottom = bottom
        return self

    def show_header_bottom(self, flag: bool):
        """Show/hide the header bottom."""
        self._header.show_bottom = flag
        return self

    # ========================================================================
    # Items Settings
    # ========================================================================

    def set_items_paddings(self, padding: Tuple[int, int, int, int]):
        """Set the paddings of the items."""
        left, right, top, bottom = padding

        self._items.style.padding.left = left
        self._items.style.padding.right = right
        self._items.style.padding.top = top
        self._items.style.padding.bottom = bottom
        return self

    def show_item_top(self, item_text: str, flag: bool):
        if not isinstance(item_text, str) and hasattr(item_text, "text"):
            item_text = item_text.text
        self._items.show_item_top(item_text, flag)
        return self

    def show_item_bottom(self, item_text: str, flag: bool):
        if not isinstance(item_text, str) and hasattr(item_text, "text"):
            item_text = item_text.text
        self._items.show_item_bottom(item_text, flag)
        return self

    # ========================================================================
    # Prologue Settings
    # ========================================================================
    
    def set_prologue_paddings(self, padding: Tuple[int, int, int, int]):
        """Set the paddings of the prologue."""
        left, right, top, bottom = padding

        self._prologue.style.padding.left = left
        self._prologue.style.padding.right = right
        self._prologue.style.padding.top = top
        self._prologue.style.padding.bottom = bottom
        return self

    def set_prologue_align(self, align: str):
        """Set the alignment of the prologue."""
        self._prologue.align = align
        return self

    def show_prologue_top(self, flag: bool):
        """Show/hide the prologue top."""
        self._prologue.show_top = flag
        return self

    def show_prologue_bottom(self, flag: bool):
        """Show/hide the prologue bottom."""
        self._prologue.show_bottom = flag
        return self

    # ========================================================================
    # Epilogue Settings
    # ========================================================================

    def set_epilogue_paddings(self, padding: Tuple[int, int, int, int]):
        """Set the paddings of the epilogue."""
        left, right, top, bottom = padding

        self._epilogue.style.padding.left = left
        self._epilogue.style.padding.right = right
        self._epilogue.style.padding.top = top
        self._epilogue.style.padding.bottom = bottom
        return self

    def set_epilogue_align(self, align: str):
        """Set the alignment of the epilogue."""
        self._epilogue.align = align
        return self

    def show_epilogue_top(self, flag: bool):
        """Show/hide the epilogue top."""
        self._epilogue.show_top = flag
        return self

    def show_epilogue_bottom(self, flag: bool):
        """Show/hide the epilogue bottom."""
        self._epilogue.show_bottom = flag
        return self

    # ========================================================================
    # Footer Settings
    # ========================================================================

    def set_footer_padding(self, padding: int):
        """Set the paddings of the footer."""

        self._footer.style.padding.top = padding
        return self

    # ========================================================================
    # Prompt Settings
    # ========================================================================
    @property
    def prompt(self) -> str:
        """Prompt property."""
        return self._prompt.prompt

    def set_prompt(self, prompt: str):
        self._prompt.prompt = prompt
        return self

    def get_prompt(self) -> str:
        return self._prompt.prompt

    # ========================================================================
    # Menu generation
    # ========================================================================

    def clear_data(self):
        """Clear data from previous menu.
        """
        self._header.title = None
        self._header.subtitle = None
        self._prologue.text = None
        self._epilogue.text = None
        self._items.items = None

    def format(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        prologue_text: Optional[str] = None,
        epilogue_text: Optional[str] = None,
        items: Optional[List] = None,
    ) -> str:
        """Formats the menu and return as a string.

        Args:
            title (str, optional): Title of the menu.
            subtitle (str, optional): Subtitle of the menu.
            prologue_text (str, optional): Prologue text of the menu.
            epilogue_text (str, optional): Epilogue text of the menu.
            items (list, optional): List of items.
        
        Returns:
            str: A string representation of the formatted menu.
        """
        self.clear_data()
        content = ""
        if title is not None:
            self._header.title = title
        if subtitle is not None:
            self._header.subtitle = subtitle
        sections = [self._header]
        if prologue_text is not None:
            self._prologue.text = prologue_text
            sections.append(self._prologue)
        if items is not None:
            self._items.items = items
            sections.append(self._items)
        if epilogue_text is not None:
            self._epilogue.text = epilogue_text
            sections.append(self._epilogue)
        sections.append(self._footer)
        sections.append(self._prompt)
        for section in sections:
            content += "\n".join(section.generate())
            if not isinstance(section, Prompt):
                content += "\n"
        return content + " "


class Menu:
    """Menu that allows the user to select an option.

    Args:
        title (str): Title of the menu, defaults to "Menu".
        subtitle (str, optional): Subtitle of the menu.
        prologue_text (str, optional): Text to include in the prologue
            section of the menu.
        epilogue_text (str, optional): Text to include in the epilogue
            section of the menu.
        show_exit_option (bool): Specifies wheter this menu should show
            an exit item by default. Defaults to True.
        exit_option_text (str): Text for the Exit menu item. Defaults
            to 'Exit'.
        arrow_keys (bool): Let the user use arrow keys for navigate the
            menu.

    Attributes:
        items (list): The list of Items that the menu will display.
        parent (Menu): The parent of this menu.
        current_option (int): The currently highlighted menu option.
        selected_option (int): The option that the user has most
            recently selected.
    
    Example:
        Script::

            from prototools import Menu
            from prototools.menu import Item

            menu = Menu()
            menu.add_item(Item("Item 1"))
            menu.add_item(Item("Item 2"))
            menu.run()
        
        Output::

            ┌─────────────────────────────────────────────────────────┐
            │                                                         │
            │                          Menu                           │
            │                                                         │
            │                                                         │
            │  1 - Item 1                                             │
            │  2 - Item 2                                             │
            │  3 - Exit                                               │
            │                                                         │
            │                                                         │
            └─────────────────────────────────────────────────────────┘
            >
    """

    currently_active_menu = None

    def __init__(
        self,
        title: str = "Menu",
        subtitle: Optional[str] = None,
        prologue_text: Optional[str] = None,
        epilogue_text: Optional[str] = None,
        screen: Optional[Screen] = None,
        builder: Optional[Builder] = None,
        show_exit_option: Optional[bool] = True,
        exit_option_text: str = "Exit",
        exit_option_color: Optional[Callable] = None,
        arrow_keys: bool = False,
    ) -> None:
        self.screen = screen if screen is not None else Screen()
        self.builder = builder if builder is not None else Builder()
        
        self.title = title
        self.subtitle = subtitle
        self.prologue_text = prologue_text
        self.epilogue_text = epilogue_text
        
        self.highlight = None
        self.normal = None

        self.show_exit_option = show_exit_option
        self.items = []
        
        self.parent = None
        self.exit_item = Exit(
            menu=self, text=exit_option_text, color=exit_option_color
        )
        self.current_option = 0
        self.selected_option = -1
        self.returned_value = None
        self.should_exit = False

        self.previous_active_menu = None
        self._main_thread = None
        self._running = threading.Event()

        self.arrow_keys = arrow_keys

    # ========================================================================
    # Settings Methods
    # ========================================================================

    def set_prompt(self, prompt: str) -> None:
        self.builder.set_prompt(prompt)

    def get_prompt(self) -> str:
        return self.builder.get_prompt()

    def set_style(self, border_style: str) -> None:
        self.builder.set_style(border_style)

    def set_dimension(self, width: int, height: int) -> None:
        self.builder.set_dimension(width, height)

    def set_margins(self, margins: Tuple[int, int, int, int]) -> None:
        self.builder.set_margins(margins)

    def set_paddings(self, paddings: Tuple[int, int, int, int]) -> None:
        self.builder.set_paddings(paddings)
    
    def set_subtitle_align(self, align: str) -> None:
        self.builder.set_subtitle_align(align)

    def show_header_bottom(self, flag: bool) -> None:
        self.builder.show_header_bottom(flag)

    def set_separators(self, flag:bool) -> None:
        self.builder.set_separators(flag)

    def set_item_color(self, color: Callable) -> None:
        for item in self.items:
            item._color = color

    def settings(
        self,
        dimension: Optional[Tuple[int, int]] = None,
        style: Optional[str] = None,
        color: Optional[Callable] = None,
        options_color: Optional[Callable] = None,
        separators: Optional[bool] = None,
        subtitle_align: Optional[str] = None,
        margins: Optional[Tuple[int, int, int, int]] = None,
        paddings: Optional[Tuple[int, int, int, int]] = None,
        items_paddings: Optional[Tuple[int, int, int, int]] = None,
        footer_padding: Optional[int] = None,
        header_bottom: Optional[bool] = None,
    ) -> None:
        if dimension is not None:
            self.builder.set_dimension(*dimension)
        if style is not None:
            self.builder.set_style(style)
        if color is not None:
            self.builder.set_color(color)
        if options_color is not None:
            self.set_item_color(options_color)
        if separators is not None:
            self.builder.set_separators(separators)
        if subtitle_align is not None:
            self.builder.set_subtitle_align(subtitle_align)
        if margins is not None:
            self.builder.set_margins(margins)
        if paddings is not None:
            self.builder.set_paddings(paddings)
        if items_paddings is not None:
            self.builder.set_items_paddings(items_paddings)
        if footer_padding is not None:
            self.builder.set_footer_padding(footer_padding)
        if header_bottom is not None:
            self.builder.show_header_bottom(header_bottom)

    # ========================================================================

    def _clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
    
    def _wait(self):
        """Wait for an action after a function has done its job."""
        print("\nPress any key to continue...")
        return msvcrt.getch() if os.name == "nt" else input()

    @property
    def current_item(self):
        """The item corresponding to the menu option that is currently
        highlighted, or None.
        """
        if self.items:
            return self.items[self.current_option]
        else:
            return None

    @property
    def selected_item(self):
        """The item in items that the user most recently selected, or
        None.
        """
        if self.items and self.selected_option != -1:
            return self.items[self.current_option]
        else:
            return None

    def add_exit(self) -> bool:
        """Add the exit item if necessary.

        Returns:
            bool: True if the exit item was added, False otherwise.
        """
        if not self.items or self.items[-1] is not self.exit_item:
            self.items.append(self.exit_item)
            return True
        return False

    def remove_exit(self) -> bool:
        """Remove the exit item if necessary.

        Returns:
            bool: True if the exit item was removed, False otherwise.
        """
        if self.items:
            if self.items[-1] is self.exit_item:
                del self.items[-1]
                return True
        return False

    def add_item(self, item: Type["Item"]) -> None:
        """Add an item to the end of the menu before the exit item.

        Args:
            item (Item): Item to be added.
        """
        did_remove = self.remove_exit()
        item.menu = self
        self.items.append(item)
        if did_remove:
            self.add_exit()

    def add_items(self, items: list) -> None:
        """Add items to the end of the menu before the exit item.

        Args:
            items (list): Items to be added.
        """
        did_remove = self.remove_exit()
        if not isinstance(items, (list, tuple)):
            raise TypeError("Menu items to be added must be type list or tuple.")
        for item in items:
            item.menu = self
            self.items.append(item)
        if did_remove:
            self.add_exit()

    def add_option(self, text: str, function: Callable, args: Any) -> None:
        """Add an option to the menu."""
        if not isinstance(text, str):
            raise TypeError("Menu option text must be type str.")
        if not callable(function):
            raise TypeError("Menu option function must be callable.")
        if args is not None:
            item = FunctionItem(
                text=text, function=function, args=args, menu=self,
            )
        else:
            item = FunctionItem(text=text, function=function, menu=self)
        self.add_item(item)

    def add_options(self, *args) -> None:
        """Add the options with their funcionality to the menu."""
        if not isinstance(args, (list, tuple)):
                raise TypeError(
                    "Menu options must be type list or tuple of tuples."
                )
        for i, arg in enumerate(args):
            if not isinstance(arg[0], str):
                raise TypeError("Menu option text must be type str.")
            if not callable(arg[1]):
                raise TypeError("Menu option function must be callable.")
            if len(arg) > 2:
                item = FunctionItem(
                    text=arg[0], function=arg[1], args=arg[2:], menu=self,
                )
            else:
                item = FunctionItem(
                    text=arg[0], function=arg[1], menu=self,
                )
            self.add_item(item)

    def remove_item(self, item: Type["Item"]) -> bool:
        """Remove the specified item from the menu.

        Args:
            item (Item): Item to be removed.
        
        Returns:
            bool: True if the item was removed, False otherwise.
        """
        for index, _item in enumerate(self.items):
            if item == _item:
                del self.items[index]
                return True
        return False

    def is_selected_item_exit(self) -> bool:
        return self.selected_item and self.selected_item is self.exit_item

    def draw(self) -> None:
        """Refresh the screen and redraw the menu. Should be called
        whenever something changes that needs to be redraw.
        """
        self.screen.printf(
            self.builder.format(
                title=self.get_title(),
                subtitle=self.get_subtitle(),
                prologue_text=self.get_prologue_text(),
                epilogue_text=self.get_epilogue_text(),
                items=self.items,
            )
        )

    def is_running(self) -> bool:
        """Check if the menu has been started and is not paused.

        Returns:
            bool: True if the menu is started and hasn't been paused;
                False otherwise.
        """
        return self._running.is_set()

    def wait_for_start(self, timeout: Optional[int] = None) -> bool:
        """Block until the menu is started.

        Args:
            timeout (int, optional): How long to wait before timing
                out.
        
        Returns:
            bool: False if timeout is given and operation times out;
                True otherwise.
        """
        return self._running.wait(timeout)

    def is_alive(self) -> bool:
        """Check the thread condition.

        Returns:
            bool: True if the thread is still alive; False otherwise.
        """
        return self._main_thread.is_alive()

    def pause(self) -> None:
        """Temporarily pause the menu until resume is called."""
        self._running.clear()

    def resume(self) -> None:
        """Set the currently active menu to this one and resumes it."""
        Menu.currently_active_menu = self
        self._running.set()

    def join(self, timeout: Optional[int] = None) -> None:
        """Should be called at some point after `Menu.start()` to block
        until the menu exits.

        Args:
            timeout (int, optional): How long to wait before timing
                out.
        """
        self._main_thread.join(timeout=timeout)

    def _wrap_start(self) -> None:
        self._mainloop()
        Menu.currently_active_menu = None
        self.clear_screen()
        Menu.currently_active_menu = self.previous_active_menu

    def start(self, show_exit_option: Optional[bool] = None) -> None:
        """Start the menu in a new thread and allow the user to
        interact with it.
        The thread is a daemon, so `Menu.join()` should be called if
        there is a possibility that the main thread will exit before
        the menu is done.

        Args:
            show_exit_option (bool, optional): Specify wheter the exit
                item should be shown, defaults to the value set in the
                initializer.
        """
        self.previous_active_menu = Menu.currently_active_menu
        Menu.currently_active_menu = None

        self.should_exit = False
        
        if show_exit_option is None:
            show_exit_option = self.show_exit_option

        if show_exit_option:
            self.add_exit()
        else:
            self.remove_exit()
        try:
            self._main_thread = threading.Thread(
                target=self._wrap_start, daemon=True
            )
        except TypeError:
            self._main_thread = threading.Thread(target=self._wrap_start)
            self._main_thread.daemon = True
        self._main_thread.start()

    def _mainloop(self) -> None:
        Menu.currently_active_menu = self
        self._running.set()

        position = 0
        event = ""
        while self._running.wait() is not False and not self.should_exit:
            self.screen.clear()
            self.draw()
            self.process_user_input()

    def run(self, show_exit_option: Optional[bool] = None) -> None:
        """Call start and then inmediately joins.

        Args:
            show_exit_option (bool, optional): Specify wheter the exit
                item should be shown, defaults to the value set in the
                initializer. 
        """
        self.start(show_exit_option)
        self.join()

    def exit(self) -> None:
        """Signal the menu to exit, then block until it's done cleaning
        up.
        """
        self.should_exit = True
        self.join()

    def select(self) -> None:
        """Select the current item and run it."""
        self.selected_option = self.current_option
        self.selected_item.set_up()
        self.selected_item.action()
        self.selected_item.clean_up()
        self.returned_value = self.selected_item.get_return()
        self.should_exit = self.selected_item.should_exit
        if not self.should_exit:
            self._wait()

    def get_input(self) -> str:
        """Can be overriden to change the input method."""
        if not self.arrow_keys:
            return self.screen.input("> ")
        
        return get_option(self.items, self) + 1

    def process_user_input(self) -> int:
        """Get the user input and decides what to do with it."""
        user_input = self.get_input()

        try:
            option = int(user_input)
        except Exception:
            return
        if 0 < option < len(self.items) + 1:
            self.current_option = option - 1
            self.select()
        
        return user_input

    def clear_screen(self) -> None:
        """Clear the screen belonging to this menu."""
        self.screen.clear()

    def get_title(self) -> str:
        """Get the title"""
        return self.title() if callable(self.title) else self.title

    def get_subtitle(self) -> str:
        """Get the subtitle"""
        return self.subtitle() if callable(self.subtitle) \
            else self.subtitle

    def get_prologue_text(self) -> str:
        """Get the prologue text"""
        return self.prologue_text() if callable(self.prologue_text) \
            else self.prologue_text

    def get_epilogue_text(self) -> str:
        """Get the epilogue text"""
        return self.epilogue_text() if callable(self.epilogue_text) \
            else self.epilogue_text

    def __repr__(self) -> str:
        return f"{self.get_title()}: {self.get_subtitle()}. {len(self.items)}"


class Item:
    """Generic menu item.

    Args:
        text (str): Text shown for this menu item.
        menu (Menu, optional): The menu to which this item belongs.
        should_exit (bool, optional): Whether the menu should exit once
            this item's action is done.
        color (Callable, optional): Returns a colored string.

    Example:

        >>> option_1 = Item("Open files")
        >>> option_2 = Item("Send files")
        >>> option_3 = Item("Delete files")
    """

    def __init__(
        self,
        text: str,
        menu: Optional[Menu] = None,
        should_exit: Optional[bool] = None,
        color: Optional[Callable] = None,
    ) -> None:
        self.text = text
        self.menu = menu
        self.should_exit = should_exit
        self._color = color if color is not None else None

    def _c(self, text):
        if self._color is not None:
            return self._color(text)
        return text


    def get_text(self) -> str:
        """Get the text in case method reference."""
        return self.text() if callable(self.text) else self.text

    def show(self, index: int) -> str:
        """How this item should be displayed in the menu.

        Args:
            index (int): Item's index in the items list of the menu.

        Returns:
            str: The representation of the item to be shown in a menu.

        Default is::

            1 - Item
            2 - Another Item
        """
        return self._c(f"{index + 1} - {self.get_text()}")

    def menu_prompt(self):
        return f"{self.menu.get_prompt()}"

    def get_return(self) -> Any: 
        """Override to change what the item returns"""
        return self.menu.returned_value

    def set_up(self) -> None: 
        """Override to add any setup actions"""
        pass

    def action(self) -> None: 
        """Override to carry out the main action"""
        pass
    
    def clean_up(self) -> None: 
        """Override to add any cleanup action"""
        pass
    
    def __eq__(self, other: object) -> bool:
        return (
            self.text == other.text and 
            self.menu == other.menu and 
            self.should_exit == other.should_exit
        )

    def __str__(self) -> str:
        return f"{self.menu.get_title()}|{self.menu_prompt()} {self.get_text()}"


class Exit(Item):
    """Used to exit the current menu.

    Args:
        text (str): Text to be shown, defaults 'Exit'.
        menu (Menu, optional): Menu to which this item belongs.
        color (Callable, optional): Returns a colored string.
    """

    def __init__(
        self, 
        text: str = "Exit",
        menu: Optional[Menu] = None,
        color: Optional[Callable] = None,
    ) -> None:
        super().__init__(text, menu=menu, should_exit=True, color=color)

    def show(self, index: int) -> str:
        """Override this method to display appropriate Exit or Return.
        """
        if self.menu and self.menu.parent and self.get_text() == "Exit":
            self.text = f"Return to {self.menu.parent.get_title()}"
        return super().show(index)


class Submenu(Item):
    """A menu item to open a submenu.
    
    Args:
        text (str): The text shown for this menu item.
        submenu (Submenu): Submenu to be opened.
        menu (Menu, optional): Menu to which this item belongs.
        should_exit (bool): Wheter the menu should exit once this
            item's action is done.
    """

    def __init__(
        self,
        text: str,
        submenu: Type["Submenu"],
        menu: Optional[Menu] = None,
        should_exit: bool = False,
    ) -> None:
        super().__init__(text, menu=menu, should_exit=should_exit)
        self.submenu = submenu
        if menu:
            self.get_submenu().parent = menu

    def set_menu(self, menu: Menu) -> None:
        """Set the menu of this item.

        Should be used instead of directly accessing the menu attribute
        for this class.

        Args:
            menu (Menu): The menu.
        """
        self.menu = menu
        self.get_submenu().parent = menu

    def set_up(self) -> None:
        """This class overrides this method"""
        self.menu.pause()
        self.menu.clear_screen()

    def action(self) -> None:
        """This class overrides this method"""
        self.get_submenu().start()

    def clean_up(self) -> None:
        """This class overrides this method"""
        self.get_submenu().join()
        self.menu.clear_screen()
        self.menu.resume()

    def get_return(self) -> Any:
        """Return the value in the submenu"""
        return self.get_submenu().returned_value

    def get_submenu(self) -> Any:
        """Unwrap the submenu variable in case it's a reference to a method"""
        return self.submenu if not callable(self.submenu) else self.submenu()


class ExternalItem(Item):
    """Base class for items that need to do stuff on the console
    outside of the console menu. Sets the terminal back to standard
    mode until the action is done. Should probably be subclassed.

    Args:
        text (str): The text shown for this menu item.
        menu (Menu, optional): The menu to which this item belongs.
        should_exit (bool): Wheter the menu should exit once this
            item's action is done.
    """

    def __init__(
        self,
        text: str,
        menu: Optional[Menu] = None,
        should_exit: bool = False,
    ) -> None:
        super().__init__(text, menu=menu, should_exit=should_exit)

    def set_up(self) -> None:
        """This class overrides this method."""
        self.menu.pause()
        self.menu.clear_screen()

    def clean_up(self) -> None:
        """This class overrides this method."""
        self.menu.clear_screen()
        self.menu.resume()


class FunctionItem(ExternalItem):
    """A menu item to call a function.

    Args:
        text (str): The text shown for this menu item.
        function (Callable): The function to be called.
        args (List[Any]): An optional list of arguments to be passed to
            the function.
        kwargs (Dict[Any]): An optional dictionary of keyword arguments
            to be passed to the function.
        menu (Menu): The menu to which this item belongs.
        should_exit (bool): Wheter the menu should exit once this
            item's action is done.
    """

    def __init__(
        self,
        text: str,
        function: Callable,
        args: List[Any] = None,
        kwargs: Dict[Any, None] = None,
        menu: Optional[Menu] = None,
        should_exit: Optional[bool] = False,
    ) -> None:
        super().__init__(text, menu=menu, should_exit=should_exit)
        self.function = function

        if args is not None:
            self.args = args
        else:
            self.args = []
        if kwargs is not None:
            self.kwargs = kwargs
        else:
            self.kwargs = {}
        
        self.return_value = None

    def action(self) -> None:
        """This class overrides this method."""
        self.return_value = self.function(*self.args, **self.kwargs)

    def clean_up(self) -> None:
        """This class overrides this method."""
        self.menu.resume()

    def get_return(self) -> Any:
        """The return value from the function call."""
        return self.return_value