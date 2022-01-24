"""This module holds helper enums for the keyboard and mouse buttons and keys
to reduce the ambiguity in the naming."""
from enum import Enum


class Keyboard(Enum):
    """An enum to hold the keyboard key names"""
    ALT = "mod1"
    CTRL = "control"
    SPACE = "space"
    ENTER = "Return"
    RETURN = "Return"
    SHIFT = "shift"
    SUPER = "mod4"
    TAB = "Tab"

# Set the default modifier key for qtile
MOD = Keyboard.SUPER


class Mouse(Enum):
    """An enum to hold the mouse button names"""
    LEFT = "Button1"
    RIGHT = "Button3"
    MIDDLE = "Button2"
