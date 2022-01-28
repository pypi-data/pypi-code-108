from colormath.color_objects import sRGBColor, HSVColor
from colormath.color_conversions import convert_color
from matplotlib.colors import to_rgb


def adjust_hsv(color, h=0., s=0., v=0.):
    hsv = convert_color(sRGBColor(*to_rgb(color)), HSVColor)
    hsv.hsv_h += h
    hsv.hsv_s += s
    hsv.hsv_v += v
    return convert_color(hsv, sRGBColor).get_value_tuple()


def set_hsv(color, h=None, s=None, v=None):
    hsv = convert_color(sRGBColor(*to_rgb(color)), HSVColor)
    if h is not None:
        hsv.hsv_h = h
    if s is not None:
        hsv.hsv_s = s
    if v is not None:
        hsv.hsv_v = v
    return convert_color(hsv, sRGBColor).get_value_tuple()
