import numpy as np
import matplotlib.colors

from scipy.interpolate import interp1d


class ColorMix:
    def __init__(self, scale, hex_colors):
        self.__scale = scale
        self.__hex_colors = np.array(hex_colors)
        self.__rgb_colors = np.array([hex_to_rgb(color) for color in self.__hex_colors])
        self.r = interp1d(self.__scale, self.__rgb_colors[:, 0])
        self.g = interp1d(self.__scale, self.__rgb_colors[:, 1])
        self.b = interp1d(self.__scale, self.__rgb_colors[:, 2])

    def rgb_color(self, scale_value):
        scale_value = np.clip(scale_value, np.min(self.__scale), np.max(self.__scale))
        rgb = (
            np.clip(self.r(scale_value), 0, 1),
            np.clip(self.g(scale_value), 0, 1),
            np.clip(self.b(scale_value), 0, 1),
        )

        return rgb

    def hex_color(self, scale_value):
        rgb = self.rgb_color(scale_value)
        hex_ = rgb_to_hex(rgb)

        return hex_


def hex_to_rgb(h: str) -> tuple:
    """
    Converts an hex color code to rgb tuple.
    """
    return tuple(int(h.replace("#", "")[i : i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    rgb = [int(255 * x) for x in rgb]
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def define_colormap(color_list: list) -> matplotlib.colors.ListedColormap:
    """
    Receives a list of hex colors an defines an matplotlib color map.
    """

    color_list = list(map(hex_to_rgb, color_list))

    cim = np.transpose(
        np.array(
            [
                np.concatenate(
                    [
                        np.linspace(color_list[j][i], color_list[j + 1][i], 100)
                        for j in range(len(color_list) - 1)
                    ]
                )
                for i in range(3)
            ]
        )
    )

    cmap = matplotlib.colors.ListedColormap(cim)

    return cmap
