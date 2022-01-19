from django.conf import settings
from psu_base.classes.Log import Log
import sass
import re

log = Log()

# --------------------------------------------
# FUNCTIONS CALLED AT TIME OF SASS COMPILATION
#
#   These must be listed in settings.py as
#      SASS_PROCESSOR_CUSTOM_FUNCTIONS
#
# --------------------------------------------


def get_sass_color(var_name, default):
    """
    :param var_name: SASS variable name (i.e. PRIMARY_BG_COLOR)
    :param default:  Default value (if not defined in sass_variables.py)
    :return: SassColor object
    """
    log.trace([var_name, default, type(default)])
    result = None
    try:
        if hasattr(settings, var_name):
            result = settings.__getattr__(var_name)
    except Exception as ee:
        log.error(f"Error getting SASS color: {ee}")

    # Convert to SassColor
    result = convert_sass_color(result if result else default)

    log.end(result)
    return result


def get_sass_string(var_name, default):
    """
    :param var_name: SASS variable name (i.e. PRIMARY_FONT)
    :param default:  Default value (if not defined in sass_variables.py)
    :return: A string to be used as SASS variable
    """
    log.trace([var_name, default])

    result = None
    try:
        if hasattr(settings, var_name):
            result = settings.__getattr__(var_name)
    except Exception as ee:
        log.error(f"Error getting SASS string: {ee}")
        result = None

    if not result:
        result = default

    log.end(result)
    return result


# --------------------------------------------
# PRIVATE FUNCTIONS
#   These are used by the functions defined
#   above, and are not called directly from
#   outside this service (Except for the demo
#   template view which prints PSU colors)
# --------------------------------------------


def convert_sass_color(given_value):
    """
    :param given_value: A color name, hx code, SassColor, or rgb[a] tuple
    :return: a SassColor object
    """
    log.trace(given_value)

    alpha_numeric_string = None
    if type(given_value) is str:
        alpha_numeric_string = re.sub(r"[^a-zA-Z0-9]+", "", given_value.lower())

    sass_color = None
    hex_color = None
    rgba_color = None

    try:
        # If None given, default will be used
        if given_value is None:
            pass

        # If given value is already SassColor, use it
        elif type(given_value) is sass.SassColor:
            sass_color = given_value

        # HTML Color Code (ie red, maroon, mediumturquoise)
        elif alpha_numeric_string and alpha_numeric_string in HTML_COLORS:
            rgba_color = HTML_COLORS[alpha_numeric_string] + (1,)

        # RGB or RGBA Tuple
        elif type(given_value) is tuple:
            if len(given_value) == 3:
                rgba_color = given_value + (1,)
            elif len(given_value) == 4:
                rgba_color = given_value

        elif given_value and type(given_value) is str and given_value.startswith("#"):
            hex_color = given_value
            rgba_color = rgba_from_hex(hex_color)

        # No other formats are accounted for yet
        else:
            log.error(f"Unexpected color format: {given_value}")
            log.debug(
                "Currently only handling HTML color names, hex codes, and RGB or RGBA tuples"
            )

        if rgba_color:
            log.trace(rgba_color, "sass.SassColor")
            sass_color = sass.SassColor(*rgba_color)

    except Exception as ee:
        log.error(f"Error converting SASS color: {ee}")

    log.end(sass_color)
    return sass_color


def hex_from_rgb(rgb_color):
    return "#%02x%02x%02x" % rgb_color


def rgb_from_hex(hex_color):
    color_code = hex_color.lstrip("#")
    return tuple(int(color_code[i : i + 2], 16) for i in (0, 2, 4))


def rgba_from_hex(hex_color):
    return rgb_from_hex(hex_color) + (1,)


HTML_COLORS = {
    # Official PSU Colors
    # https://www.pdx.edu/university-communications/sites/www.pdx.edu.university-communications/files/2017_02_IdentityGlance_0.pdf
    "psugreen": (106, 127, 16),
    "psuaccentgreen": (168, 180, 0),
    "psubrown": (96, 53, 29),
    "psusienna": (163, 63, 31),
    "psured": (210, 73, 42),
    "psuorange": (220, 155, 50),
    "psuyellow": (230, 220, 143),
    "psutan": (232, 211, 162),
    "psugray": (71, 67, 52),
    "psupurple": (101, 3, 96),
    "psublue": (0, 117, 154),
    "psulightblue": (161, 216, 224),
    # Standard Web Colors
    "lightsalmon": (255, 160, 122),
    "salmon": (250, 128, 114),
    "darksalmon": (233, 150, 122),
    "lightcoral": (240, 128, 128),
    "indianred": (205, 92, 92),
    "crimson": (220, 20, 60),
    "firebrick": (178, 34, 34),
    "red": (255, 0, 0),
    "darkred": (139, 0, 0),
    "coral": (255, 127, 80),
    "tomato": (255, 99, 71),
    "orangered": (255, 69, 0),
    "gold": (255, 215, 0),
    "orange": (255, 165, 0),
    "darkorange": (255, 140, 0),
    "lightyellow": (255, 255, 224),
    "lemonchiffon": (255, 250, 205),
    "lightgoldenrodyellow": (250, 250, 210),
    "papayawhip": (255, 239, 213),
    "moccasin": (255, 228, 181),
    "peachpuff": (255, 218, 185),
    "palegoldenrod": (238, 232, 170),
    "khaki": (240, 230, 140),
    "darkkhaki": (189, 183, 107),
    "yellow": (255, 255, 0),
    "lawngreen": (124, 252, 0),
    "chartreuse": (127, 255, 0),
    "limegreen": (50, 205, 50),
    "lime": (0, 255, 0),
    "forestgreen": (34, 139, 34),
    "green": (0, 128, 0),
    "darkgreen": (0, 100, 0),
    "greenyellow": (173, 255, 47),
    "yellowgreen": (154, 205, 50),
    "springgreen": (0, 255, 127),
    "mediumspringgreen": (0, 250, 154),
    "lightgreen": (144, 238, 144),
    "palegreen": (152, 251, 152),
    "darkseagreen": (143, 188, 143),
    "mediumseagreen": (60, 179, 113),
    "seagreen": (46, 139, 87),
    "olive": (128, 128, 0),
    "darkolivegreen": (85, 107, 47),
    "olivedrab": (107, 142, 35),
    "lightcyan": (224, 255, 255),
    "cyan": (0, 255, 255),
    "aqua": (0, 255, 255),
    "aquamarine": (127, 255, 212),
    "mediumaquamarine": (102, 205, 170),
    "paleturquoise": (175, 238, 238),
    "turquoise": (64, 224, 208),
    "mediumturquoise": (72, 209, 204),
    "darkturquoise": (0, 206, 209),
    "lightseagreen": (32, 178, 170),
    "cadetblue": (95, 158, 160),
    "darkcyan": (0, 139, 139),
    "teal": (0, 128, 128),
    "powderblue": (176, 224, 230),
    "lightblue": (173, 216, 230),
    "lightskyblue": (135, 206, 250),
    "skyblue": (135, 206, 235),
    "deepskyblue": (0, 191, 255),
    "lightsteelblue": (176, 196, 222),
    "dodgerblue": (30, 144, 255),
    "cornflowerblue": (100, 149, 237),
    "steelblue": (70, 130, 180),
    "royalblue": (65, 105, 225),
    "blue": (0, 0, 255),
    "mediumblue": (0, 0, 205),
    "darkblue": (0, 0, 139),
    "navy": (0, 0, 128),
    "midnightblue": (25, 25, 112),
    "mediumslateblue": (123, 104, 238),
    "slateblue": (106, 90, 205),
    "darkslateblue": (72, 61, 139),
    "lavender": (230, 230, 250),
    "thistle": (216, 191, 216),
    "plum": (221, 160, 221),
    "violet": (238, 130, 238),
    "orchid": (218, 112, 214),
    "fuchsia": (255, 0, 255),
    "magenta": (255, 0, 255),
    "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 112, 219),
    "blueviolet": (138, 43, 226),
    "darkviolet": (148, 0, 211),
    "darkorchid": (153, 50, 204),
    "darkmagenta": (139, 0, 139),
    "purple": (128, 0, 128),
    "indigo": (75, 0, 130),
    "pink": (255, 192, 203),
    "lightpink": (255, 182, 193),
    "hotpink": (255, 105, 180),
    "deeppink": (255, 20, 147),
    "palevioletred": (219, 112, 147),
    "mediumvioletred": (199, 21, 133),
    "white": (255, 255, 255),
    "snow": (255, 250, 250),
    "honeydew": (240, 255, 240),
    "mintcream": (245, 255, 250),
    "azure": (240, 255, 255),
    "aliceblue": (240, 248, 255),
    "ghostwhite": (248, 248, 255),
    "whitesmoke": (245, 245, 245),
    "seashell": (255, 245, 238),
    "beige": (245, 245, 220),
    "oldlace": (253, 245, 230),
    "floralwhite": (255, 250, 240),
    "ivory": (255, 255, 240),
    "antiquewhite": (250, 235, 215),
    "linen": (250, 240, 230),
    "lavenderblush": (255, 240, 245),
    "mistyrose": (255, 228, 225),
    "gainsboro": (220, 220, 220),
    "lightgray": (211, 211, 211),
    "silver": (192, 192, 192),
    "darkgray": (169, 169, 169),
    "gray": (128, 128, 128),
    "dimgray": (105, 105, 105),
    "lightslategray": (119, 136, 153),
    "slategray": (112, 128, 144),
    "darkslategray": (47, 79, 79),
    "black": (0, 0, 0),
    "cornsilk": (255, 248, 220),
    "blanchedalmond": (255, 235, 205),
    "bisque": (255, 228, 196),
    "navajowhite": (255, 222, 173),
    "wheat": (245, 222, 179),
    "burlywood": (222, 184, 135),
    "tan": (210, 180, 140),
    "rosybrown": (188, 143, 143),
    "sandybrown": (244, 164, 96),
    "goldenrod": (218, 165, 32),
    "peru": (205, 133, 63),
    "chocolate": (210, 105, 30),
    "saddlebrown": (139, 69, 19),
    "sienna": (160, 82, 45),
    "brown": (165, 42, 42),
    "maroon": (128, 0, 0),
}
