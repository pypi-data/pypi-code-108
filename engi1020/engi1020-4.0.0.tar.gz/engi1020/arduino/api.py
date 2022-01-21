"""Student-visible API for Arduino programming in labs.

This module re-exports selected functions and values from other modules to hide
some of the overall module's complexity. It can be imported with:

from engi1020.arduino.api import *

"""

from .io import analog_read, analog_write, digital_read, digital_write, buzzer_frequency, buzzer_note, buzzer_stop
from .oled import clear as oled_clear, print_message as oled_print, move_cursor as oled_move_cursor
from .rgb_lcd import (
        clear as rgb_lcd_clear,
        set_colour as rgb_lcd_colour,
)
