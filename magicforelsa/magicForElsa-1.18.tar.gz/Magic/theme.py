import os
from tkinter.colorchooser import askcolor

initpth = os.getcwd() + "/resources/ initial.elsa"


def read_theme() -> tuple:
    """Reads the theme from the initial.elsa file"""
    try:
        with open(initpth) as f: datas = f.read()
        colours = datas.split(";")
        bg_colour, text_color, button_colour = colours[0].rstrip().lstrip(), colours[1].rstrip().lstrip(), \
                                               colours[2].split("\n")[0].rstrip().lstrip()
        return bg_colour, text_color, button_colour
    except Exception as e: print("initial.elsa is corrupted", e)


def theme_writer(bg_colour: str, font_colour: str, button_colour: str) -> None:
    """To write the new theme"""
    with open(initpth, "w") as f:
        f.write(f"{bg_colour};{font_colour};{button_colour}\n#The order is bg,font color,button colour\n#Please remember to use ';' to separate colours")


def newcolorevent(index: int) -> None:
    """To add a new colour"""
    bg_colour, text_color, button_colour = read_theme()
    if (color := askcolor()[1]) is not None:
        match index:
            case 0: theme_writer(color, text_color, button_colour)
            case 1: theme_writer(bg_colour, color, button_colour)
            case 2: theme_writer(bg_colour, text_color, color)


new_background_colour = lambda event = "": newcolorevent(0)  # New bg color
new_font_colour = lambda event = "": newcolorevent(1)  # New font color
new_button_colour = lambda event = "": newcolorevent(2)  # New button colour
