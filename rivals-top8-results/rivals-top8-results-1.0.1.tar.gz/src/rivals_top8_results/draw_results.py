from datetime import datetime
import os
import sys

import numpy as np

from PIL import Image, ImageDraw, ImageFont

# useful for offset testing purposes
def draw_top16(size):
    layout_rgb = (0, 230, 200)

    players = [
        draw_portrait("AAAAAAAA", "Zetterburn", "Default", 1, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Wrastor", "Default", 2, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Sylvanos", "Default", 3, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Shovel Knight", "Default", 4, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Ranno", "Default", 5, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Ori", "Default", 5, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Orcane", "Default", 7, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Maypul", "Default", 7, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Kragg", "Default", 9, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Forsburn", "Default", 9, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Etalus", "Default", 9, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Elliana", "Default", 9, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Clairen", "Default", 12, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Absa", "Default", 12, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "Random", "Default", 12, 2, layout_rgb, size),
        draw_portrait("AAAAAAAA", "", "Default", 12, 2, layout_rgb, size),
    ]

    output = Image.new("RGBA", (players[0].size[0] * 4, players[0].size[1] * 4))

    for i, p in enumerate(players):
        if i == 0:
            output.paste(p, (0, 0), p)
        elif i <= 3:
            output.paste(p, (p.size[0] * i, 0), p)
        elif i > 3 and i <= 7:
            output.paste(p, (p.size[0] * i - p.size[0] * 4, p.size[1]), p)
        elif i > 7 and i <= 11:
            output.paste(p, (p.size[0] * i - p.size[0] * 4 * 2, p.size[1] * 2), p)
        elif i > 11 and i <= 15:
            output.paste(p, (p.size[0] * i - p.size[0] * 4 * 3, p.size[1] * 3), p)

    output.save("output.png")


def draw_top8_popup():
    layout_rgb = (0, 230, 200)

    players = [
        draw_portrait("AAAAAAAA", "Zetterburn", "Default", 1, 3, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Wrastor", "Default", 2, 1.6, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Sylvanos", "Default", 3, 1.6, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Shovel Knight", "Default", 4, 1.6, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Ranno", "Default", 5, 1.2, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Ori", "Default", 5, 1.2, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Orcane", "Default", 7, 1.2, layout_rgb, "L"),
        draw_portrait("AAAAAAAA", "Maypul", "Default", 7, 1.2, layout_rgb, "L"),
    ]

    output = Image.new(
        "RGBA", (players[0].size[0] + players[1].size[0] * 3, players[0].size[1])
    )

    for i, p in enumerate(players):
        if i == 0:
            output.paste(p, (0, 0), p)
        elif i >= 0 and i <= 3:
            output.paste(
                p, (players[0].size[0] + players[1].size[0] * (i - 1), 0 + 104), p
            )
        elif i > 3:
            output.paste(
                p,
                (
                    players[0].size[0] + players[4].size[0] * (i - 4),
                    players[1].size[1] + 104,
                ),
                p,
            )

    output.save("output.png")


def draw_top8(
    nicknames,
    characters,
    skins,
    secondaries,
    tertiaries,
    resize_factor,
    layout_rgb=(255, 138, 132),
    bg_opacity=100,
    save=True,
):
    # layout settings (from last player to first player)
    placements = [1, 2, 3, 4, 5, 5, 7, 7]
    resizes = [1.223, 0.9, 0.9, 0.9, 0.675, 0.675, 0.675, 0.675]
    sizes = ["L", "M", "M", "M", "S", "S", "S", "S"]

    # creates portraits
    players = [
        draw_portrait(
            nicknames[i],
            characters[i],
            skins[i],
            placements[i],
            resizes[i],
            layout_rgb,
            sizes[i],
            secondaries[i],
            tertiaries[i],
            bg_opacity=bg_opacity,
            save=False,
        )
        for i in range(8)
    ]

    # creates output image
    output = Image.new(
        "RGBA", (players[0].size[0] + players[1].size[0] * 3 - 4, players[0].size[1])
    )

    # pastes portraits onto top8
    # for i, p in enumerate(players):
    #     if i == 0:
    #         pasteImage(p, (0, 0), output)
    #     elif i >= 0 and i <= 3:
    #         pasteImage(p, (players[0].size[0] + players[1].size[0] * (i - 1) - 4, 0), output)
    #     elif i > 3:
    #         pasteImage(p, (players[0].size[0] + players[4].size[0] * (i - 4) - 4, players[1].size[1]), output)

    pasteImage(players[0], (0, 0), output)
    pasteImage(players[1], (players[0].size[0] - 4, 0), output)
    pasteImage(players[2], (players[0].size[0] + players[1].size[0] * 1 - 7, 0), output)
    pasteImage(
        players[3], (players[0].size[0] + players[1].size[0] * 2 - 12, 0), output
    )
    pasteImage(
        players[4],
        (players[0].size[0] + players[4].size[0] * 0 - 4, players[1].size[1]),
        output,
    )
    pasteImage(
        players[5],
        (players[0].size[0] + players[4].size[0] * 1 - 8, players[1].size[1]),
        output,
    )
    pasteImage(
        players[6],
        (players[0].size[0] + players[4].size[0] * 2 - 10, players[1].size[1]),
        output,
    )
    pasteImage(
        players[7],
        (players[0].size[0] + players[4].size[0] * 3 - 12, players[1].size[1]),
        output,
    )

    # resizes the output image
    output = output.resize(
        (int(output.size[0] * resize_factor), int(output.size[1] * resize_factor)),
        resample=Image.BOX,
    )

    if save:
        output.save("output.png")

    return output


def replace_rgb(image, old_rgb, new_rgb, return_image=True):
    img_array = np.array(image)

    r1, g1, b1 = old_rgb
    r2, g2, b2 = new_rgb

    red, green, blue = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    img_array[:, :, :3][mask] = [r2, g2, b2]

    if return_image:
        img_array = Image.fromarray(img_array)

    return img_array


def pasteImage(img, posn, bigim):
    # needed to correctly paste images with alpha
    pixdata = img.load()
    width, height = img.size
    mainpixdata = bigim.load()

    for y in range(height):
        for x in range(width):
            if pixdata[x, y] != (0, 0, 0, 0):
                mainpixdata[x + posn[0], y + posn[1]] = pixdata[x, y]


def centered_pos(pos1, pos2):
    W, H = pos1.size
    w, h = pos2.size

    return (int((W - w) / 2), int((H - h) / 2))


def draw_rectangle(image, rgb, top_left, bot_right):
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle([top_left, bot_right], fill=(rgb))

    return image


def draw_text(image, text, rgb, font_size, bot_right, center_text=False):
    font_dir = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\Resources\Layout\Pixellari.ttf"

    draw = ImageDraw.Draw(image, "RGBA")
    font = ImageFont.truetype(font_dir, font_size)  # TODO: add a font parameter

    if center_text:
        W, H = bot_right
        w, h = draw.textsize(str(text), font)

        draw.text(((W - w) / 2, (H - h) / 2), str(text), fill=rgb, font=font)
    else:
        draw.text((bot_right[0], bot_right[1]), str(text), fill=rgb, font=font)

    return image


# used to adjust the nicknames' height
nickname_multipliers = {"L": 1.88, "M": 1.85, "S": 1.83}

# used to pick the right portrait box
portrait_multipliers = {"L": 1, "M": 0.8, "S": 0.75}

# different box sizes have different zoom-ins
zoom_multipliers = {"L": 1.65, "M": 1.75, "S": 1.9}

# xy offsets
char_offsets = {
    "Absa": {
        "L": (-50, 0),
        "M": (-5, -25),
        "S": (-10, -10),
    },
    "Clairen": {
        "L": (-100, 0),
        "M": (-40, -20),
        "S": (-40, -20),
    },
    "Elliana": {
        "L": (-100, 0),
        "M": (-40, -20),
        "S": (-50, -20),
    },
    "Etalus": {
        "L": (-200, 10),
        "M": (-130, -10),
        "S": (-140, -10),
    },
    "Forsburn": {
        "L": (-160, 0),
        "M": (-80, -20),
        "S": (-80, -15),
    },
    "Kragg": {
        "L": (-140, 0),
        "M": (-90, 0),
        "S": (-70, 0),
    },
    "Maypul": {
        "L": (-120, 120),
        "M": (-30, 60),
        "S": (-60, 30),
    },
    "Orcane": {
        "L": (-160, 0),
        "M": (-80, -5),
        "S": (-95, -5),
    },
    "Ori": {
        "L": (-160, -20),
        "M": (-95, -35),
        "S": (-90, -50),
    },
    "Random": {
        "L": (-130, 0),
        "M": (-90, -20),
        "S": (-90, -40),
    },
    "Ranno": {
        "L": (-110, 10),
        "M": (-60, 10),
        "S": (-80, 0),
    },
    "Shovel Knight": {
        "L": (-100, 0),
        "M": (-35, -5),
        "S": (-40, -5),
    },
    "Shovel knight": {
        "L": (-100, 0),
        "M": (-35, -5),
        "S": (-40, -5),
    },
    "Sylvanos": {
        "L": (-150, 0),
        "M": (-90, -10),
        "S": (-95, -10),
    },
    "Wrastor": {
        "L": (-45, 0),
        "M": (-20, -20),
        "S": (-10, -40),
    },
    "Zetterburn": {
        "L": (-100, 0),
        "M": (-60, 0),
        "S": (-60, -10),
    },
    "": {"L": (0, 0), "M": (0, 0), "S": (0, 0)},
}


def open_image(input_file, size=(0, 0)):
    try:
        image = Image.open(input_file)
    except FileNotFoundError:
        print(
            "FileNotFoundError: please check your input file and try again.\n"
            fr"Current input file: {input_file}"
        )
        sys.exit(1)

    if size != (0, 0):
        image.resize(
            size[0],
            size[1],
            resample=Image.BOX,
        )

    return image


def draw_additional_char(character, portrait, position):
    char_dir = fr"{os.getcwd()}\resources\characters\Secondary"
    input_file = fr"{char_dir}\{character}.png"

    try:
        secondary = Image.open(input_file)
    except FileNotFoundError:
        print(
            "FileNotFoundError: please check your input file and try again.\n"
            fr"Current input file: {input_file}"
        )
        sys.exit(1)

    portrait.paste(secondary, position, secondary)


def draw_portrait(
    nickname,
    character,
    skin,
    placement,
    resizing,
    rgb,
    size,
    secondary=None,
    tertiary=None,
    bg_opacity=100,
    save=False,
):
    # loads images
    input_file = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\Resources/Layout/char_portrait_no_nick.png"
    layout = open_image(input_file)

    # creates new image to be used as background layer
    portrait = Image.new(
        "RGBA",
        (
            layout.size[0],
            int(layout.size[1] * portrait_multipliers[size]),
        ),
    )

    # creates opaque background behind the portrait
    draw_rectangle(portrait, (*rgb, bg_opacity), (0, 0), portrait.size)

    layout = layout.resize(
        (int(layout.size[0]), int(layout.size[1] * portrait_multipliers[size])),
        resample=Image.BOX,
    )

    # returns character image file unless no character is requested
    if character:
        char_dir = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\resources\characters\Main"
        char = open_image(fr"{char_dir}\{character}\{skin}.png")
        char = char.resize(
            (
                int(
                    (char.size[0] * zoom_multipliers[size]) * portrait_multipliers[size]
                ),
                int(
                    (char.size[1] * zoom_multipliers[size]) * portrait_multipliers[size]
                ),
            ),
            resample=Image.BOX,
        )
    else:
        char = Image.new("RGBA", (0, 0))

    # loads layout and replaces default rgb with the chosen new rgb
    layout = replace_rgb(layout, (76, 255, 0), rgb)

    # pastes character and layout onto the empty portrait
    portrait.paste(
        char,
        (
            int((char_offsets[character][size][0])),
            int((char_offsets[character][size][1])),
        ),
        char,
    )

    # pastes layout onto characters again to cover overlaps
    portrait.paste(layout, (0, 0), layout)

    # draws nickname rectangle using both top left and bottom right position
    nickname_tl = (4, portrait.size[1] - 60)
    nickname_br = (portrait.size[0] - 5, portrait.size[1] - 4)
    draw_rectangle(portrait, (255, 255, 255), nickname_tl, nickname_br)

    # draws nickname using its bottom right position
    nick_text_br = (portrait.size[0], portrait.size[1] * nickname_multipliers[size])
    draw_text(
        portrait,
        nickname,
        (0, 0, 0),
        52 if len(nickname) <= 13 else 40,
        nick_text_br,
        center_text=True,
    )

    # draws secondary
    if secondary:
        draw_additional_char(secondary, portrait, (portrait.size[0] - 85, 5))

    # draws tertiary
    if tertiary:
        draw_additional_char(tertiary, portrait, (5, portrait.size[1] - 133))

    # draws placement box
    draw_rectangle(portrait, rgb, (0, 0), (65, 65))

    # draws placement using its bottom right position
    placement_br = (65, 65)
    draw_text(portrait, placement, (255, 255, 255), 64, placement_br, center_text=True)

    # resizes portrait right before quitting
    portrait = portrait.resize(
        (int(portrait.size[0] * resizing), int(portrait.size[1] * resizing)),
        resample=Image.BOX,
    )

    # saves portrait as a separate file
    if save:
        portrait.save(f"./Portraits/{nickname}.png")

    return portrait


def draw_results(
    top8_image=Image.new("RGBA", (0, 0)),
    title="A Rivals of Aether Bracket",
    attendees_num=0,
    date=datetime.now().strftime("%d-%m-%Y"),
    layout_rgb=(255, 138, 132),
    stage="Aethereal Gates",
    stage_variant=1,
    logo=False,
    logo_offset=False,
    save=True,
):
    input_file = fr"{os.path.abspath(os.getcwd())}\\src\\rivals_top8_results\\Resources\Backgrounds\{stage}\{stage_variant}.png"

    try:
        bg = Image.open(input_file)
    except FileNotFoundError:
        print(
            "FileNotFoundError: please check your input file and try again.\n"
            fr"Current input file: {input_file}"
        )
        sys.exit(1)

    bg = bg.resize((1920, 1080), resample=Image.BOX)

    bg.paste(top8_image, centered_pos(bg, top8_image), top8_image)

    draw_rectangle(bg, layout_rgb, (0, 0), (bg.size[0], 70))
    draw_rectangle(bg, layout_rgb, (0, bg.size[1] - 70), (bg.size[0], bg.size[1]))
    draw_text(bg, f"{title}", (255, 255, 255), 68, (bg.size[0], 70), center_text=True)

    draw_text(
        bg, "graphics by @Kiirochii", (255, 255, 255), 32, (10, bg.size[1] - 70 + 35)
    )
    draw_text(
        bg, "script by @Impasse52", (255, 255, 255), 32, (10, bg.size[1] - 100 + 35)
    )

    draw_text(
        bg,
        f"{attendees_num} participants",
        (255, 255, 255),
        32,
        (bg.size[0] - 230, bg.size[1] - 100 + 35),
    )
    draw_text(
        bg, f"{date}", (255, 255, 255), 32, (bg.size[0] - 190, bg.size[1] - 70 + 35)
    )

    if logo:
        bg.paste(logo, (bg.size[0] + logo_offset[0], 0 + logo_offset[1]), logo)

    if save:
        bg.save("results.png")
