from . import command


def clear():
    """Clear the RGB-LCD display."""

    command("Clearing RGB LCD display", "Rc", "Rc-OK")


def print(row, col, message):
    """Print a message to the RGB LCD screen."

    Parameters:
      row (int): 0-1
      col (int): 0-15
      message (str): The message to print
    """

    encoded = message.encode('utf-8')

    command(f"Printing '{message}' to RGB LCD display @ ({row}, {col})",
            "Rp", "Rp-OK", bytes([row, col, len(encoded)]), encoded)


def set_colour(red, green, blue):
    """Set the backlight colour of the RGB LCD screen.

    Parameters:
      red (int): 0-255
      green (int): 0-255
      blue (int): 0-255
    """

    command(f"Setting RGB LCD backlight colour to ({red}, {green}, {blue})",
            "RC", "RC-OK", bytes([red, green, blue]))
