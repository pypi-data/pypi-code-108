import copy
import matplotlib as mpl
from PIL import Image, ImageDraw
from matplotlib import colors
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

size = 100

white = colors.to_hex("w")
black = colors.to_hex("k")
red = colors.to_hex("r")
cyan = colors.to_hex("c")
blue = colors.to_hex("b")
magenta = colors.to_hex("m")
yellow = colors.to_hex("y")
grey = (196, 196, 196)
green = colors.to_hex("g")
start_color = (76, 0, 153)
neon_green = (128, 255, 0)
light_grey = (220, 220, 220)

goal = Image.new("RGBA", (size, size), neon_green)
draw = ImageDraw.Draw(goal)
draw.rectangle(((0, 0), (size - 1, size - 1)), outline=(0, 0, 0))
start = Image.new("RGBA", (size, size), start_color)
draw = ImageDraw.Draw(start)
draw.rectangle(((0, 0), (size - 1, size - 1)), outline=(0, 0, 0))
empty = Image.new("RGBA", (size, size), white)
draw = ImageDraw.Draw(empty)
draw.rectangle(((0, 0), (size - 1, size - 1)), outline=(0, 0, 0))

wall = Image.new("RGBA", (size, size), grey)
draw = ImageDraw.Draw(wall)
draw.rectangle(((0, 0), (size - 1, size - 1)), outline=black)
draw.line((10, 10, size - 10, size - 10), fill=(0, 0, 0), width=2)
draw.line((size - 10, 10, 10, size - 10), fill=(0, 0, 0), width=2)

line_colors = [red, yellow, cyan, blue, green, black]


# specified font size
# font = ImageFont.truetype('SpaceMonoBoldItalic.ttf', 40)


def create_map(env, show_path=False, show_landmarks=False, hide_start_line=False):
    """create the map

    Args:
        env (Environment): Instance of rt game.
        show_path (bool, optional): show the taken path in the current episode. Defaults to False.
        show_landmarks (bool, optional): Mark the landmarks. Defaults to False.
        hide_start_line (bool, optional): Hide the start line. Defaults to False.

    Returns:
        PIL: graphical way to represent the current state of game
    """
    h = env.map.width
    w = env.map.height
    result = Image.new(
        "RGBA",
        (size * h, size * w),
        (
            0,
            0,
            0,
        ),
    )
    for i, line in enumerate(env.map.map):
        for j, sign in enumerate(line):
            if sign == "x":
                result.paste(wall, (j * size, i * size), mask=wall)
                continue
            if sign == "s":
                if hide_start_line:
                    result.paste(empty, (j * size, i * size), mask=empty)
                else:
                    result.paste(start, (j * size, i * size), mask=start)
                continue
            if sign == "g":
                result.paste(goal, (j * size, i * size), mask=goal)
                continue
            if sign == ".":
                if show_landmarks:
                    rgb_value = int(255 - env.potentials[i][j] * 10)
                    landmark_color = (0, 0, rgb_value)
                    landmark = Image.new("RGBA", (size, size), landmark_color)
                    draw = ImageDraw.Draw(landmark)
                    draw.rectangle(((0, 0), (size - 1, size - 1)), outline=(0, 0, 0))
                    result.paste(landmark, (j * size, i * size), mask=landmark)
                else:
                    result.paste(empty, (j * size, i * size), mask=empty)
                continue

    path = copy.copy(env.path)
    path.append(path[-1])
    color = line_colors[0]
    o = 0.5

    if show_path:

        for i in range(len(path) - 1):
            f = path[i]
            t = path[i + 1]

            draw = ImageDraw.Draw(result)
            x1 = (f[1] + o) * size
            y1 = (f[0] + o) * size
            x2 = (t[1] + o) * size
            y2 = (t[0] + o) * size
            cx1 = x1 - 15
            cx2 = x1 + 15
            cy1 = y1 - 15
            cy2 = y1 + 15
            draw.line((x1, y1, x2, y2), fill=color, width=5)
            draw.ellipse((cx1, cy1, cx2, cy2), color)

    return result


def print_heatmap(
    values,
    bounds=None,
    colormap=None,
    print_path=None,
    show=True,
    figsize=None,
    fontsize=None,
):
    """Builds a heatmap of a two dimensional array.

    :param values: 2D array from which the heatmap is generated
    :param bounds: bound array for the colors used in the heatmap
    :param colormap: a matplotlib colormap
    :param print_path: the path to where a png representation is saved
    :param show: boolean flag if the heatmap should be printed
    :returns: the figure object
    """
    if bounds is None:
        bounds = [-1, 0, 0.25, 0.5, 0.75, 0.9, 0.97, 0.99, 0.998, 1]
    if colormap is None:
        colormap = mpl.colors.ListedColormap(
            [
                "grey",
                "black",
                "red",
                "orange",
                "yellow",
                "lime",
                "limegreen",
                "green",
                "darkgreen",
            ]
        )
    norm = mpl.colors.BoundaryNorm(bounds, colormap.N)
    if figsize is None:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=figsize)
    fig.add_subplot(111)
    im = plt.pcolormesh(
        values, edgecolors="lightgray", linewidth=0.005, cmap=colormap, norm=norm
    )
    ax = plt.gca()
    plt.xticks([])
    plt.yticks([])
    ax.invert_yaxis()
    ax.set_aspect("equal")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)

    if fontsize is not None:
        cbar.ax.tick_params(labelsize=fontsize)

    if print_path is not None:
        plt.savefig(print_path)
    if show:
        plt.show()
    return fig
