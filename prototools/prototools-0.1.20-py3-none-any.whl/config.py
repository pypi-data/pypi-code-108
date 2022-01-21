HEIGHT = 40
WIDTH = 80
TERMINAL_WIDTH = 47

BORDER_TYPE = {
    0: "ascii", 
    1: "light",
    2: "heavy",
    3: "double",
    4: "borderless",
}

BORDER = {
    "top_left": {
        "ascii": "+", "borderless": " ", "arc": u"\u256d",
        "light": u"\u250C", "heavy": u"\u250F", "double": u"\u2554",
    },
    "top_right": {
        "ascii": "+", "borderless": " ", "arc": u"\u256e",
        "light": u"\u2510", "heavy": u"\u2513", "double": u"\u2557",
    },
    "bottom_left": {
        "ascii": "+", "borderless": " ", "arc": u"\u2570",
        "light": u"\u2514", "heavy": u"\u2517", "double": u"\u255A",
    },
    "bottom_right": {
        "ascii": "+", "borderless": " ", "arc": u"\u256f",
        "light": u"\u2518", "heavy": u"\u251B", "double": u"\u255D",
    },
    "vertical": {
        "ascii": "|", "borderless": " ",
        "light": u"\u2502", "heavy": u"\u2503", "double": u"\u2551",
    },
    "vertical_left": {
        "ascii": "+", "borderless": " ",
        "light": u"\u251C", "heavy": u"\u2523", "double": u"\u2560",
    },
    "vertical_right": {
        "ascii": "+", "borderless": " ",
        "light": u"\u2524", "heavy": u"\u252B", "double": u"\u2563",
    },
    "horizontal": {
        "ascii": "-", "borderless": " ",
        "light": u"\u2500", "heavy": u"\u2501", "double": u"\u2550",
    },
    "horizontal_top": {
        "ascii": "+", "borderless": " ",
        "light": u"\u252C", "heavy": u"\u2533", "double": u"\u2566",
    },
    "horizontal_bottom": {
        "ascii": "+", "borderless": " ",
        "light": u"\u2534", "heavy": u"\u253B", "double": u"\u2569",
    },
    "intersection": {
        "ascii": "+", "borderless": " ",
        "light": u"\u253C", "heavy": u"\u254B", "double": u"\u256C",
    },
}

MARGIN = {
    "left": 2,
    "right": 2,
    "top": 1,
    "bottom": 0,
}

PADDING = {
    "left": 2,
    "right": 2,
    "top": 1,
    "bottom": 1,
}