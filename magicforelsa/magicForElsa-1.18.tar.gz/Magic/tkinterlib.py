"""This  module is for stylising the Tkinter GUI"""
from functools import partial
from tkinter import Button, Label, LabelFrame
from Magic import theme
import platform

bg_colour, text_color, button_colour = theme.read_theme()


def tkinter_initialise(a, x: int = 0, y: int = 0, top: int = 1, noborders: bool = True, opacity: float = 0.9) -> None:
    """Used to mordernify tkinter gui boxes"""
    a.withdraw()  # Hide tkinter windows to finish initialization
    a.attributes("-alpha", opacity)  # Opacity of tkinter window
    if platform.system().lower() == "windows": a.overrideredirect(noborders)  # Remove Borders and default title bars
    else: a.wm_attributes('-type', 'splash') if noborders else None  # Splash screen
    a.configure(bg = bg_colour)
    a.attributes("-topmost", top)  # Decides if the tkinter windows shld always be on the top of other window
    a.geometry(f"+{x}+{y}")  # positions tkinter windows at x and y coordinate
    a.deiconify()  # show the tkinter window back


def button_hover_color(but, bgc, fgc) -> None:
    "To Change the color of the button"
    but.config(bg = bgc)
    but.config(fg = fgc)


on_enter = lambda event, but: button_hover_color(but, button_colour, bg_colour)  # Colour change when cursored over
on_leave = lambda event, but: button_hover_color(but, bg_colour, text_color)  # Colour change when cursor leaves


def reset_colors() -> None:
    "Force reset the colours when user changes theme"
    global bg_colour, text_color, button_colour
    bg_colour, text_color, button_colour = theme.read_theme()


def TButton(root: object, text: str = "", command: object | None | str = None, relief = "ridge") -> object:
    "Customised Tkinter button"
    b = Button(root, text = text, fg = text_color, bd = 0, bg = bg_colour, command = command, relief = relief)
    b.bind("<Enter>", partial(on_enter, but = b))
    b.bind("<Leave>", partial(on_leave, but = b))
    return b


TLabel = lambda root, text = '': Label(root, text = text, fg = text_color, bg = bg_colour)  # Custom tkinter label
TLabelFrame = lambda root, text = '': LabelFrame(root, text = text, fg = text_color, bg = bg_colour)  # Custom tkinter label frame
