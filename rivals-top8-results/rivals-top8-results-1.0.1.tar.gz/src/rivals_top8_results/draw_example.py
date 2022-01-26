from datetime import datetime
import json

from PIL import Image

from draw_results import draw_results, draw_top8, draw_top16

if __name__ == "__main__":
    characters = [
        "Zetterburn",
        "Kragg",
        "Zetterburn",
        "Ori",
        "Elliana",
        "Etalus",
        "Kragg",
        "Forsburn",
    ]

    secondaries = ["" for i in range(0, 8)]
    tertiaries = ["" for i in range(0, 8)]

    nicknames = [
        "Fireicey",
        "Transco",
        "Alki",
        "Kalamahri",
        "Shayd",
        "Bleblemlic",
        "Boss Hog",
        "Downiel",
    ]

    skins = [
        "Green",
        "Default",
        "Default",
        "Default",
        "Default",
        "Default",
        "Default",
        "Default",
    ]

    top8 = draw_top8(
        nicknames,
        characters,
        skins,
        secondaries,
        tertiaries,
        layout_rgb=(255, 138, 132),
        bg_opacity=100,
        resize_factor=1.3,
    )

    draw_results(
        top8,
        title="EU RCS Season 6 Finals",
        attendees_num=89,
        date="24-01-2022",
        stage="Aethereal Gates",
        stage_variant=2,
        layout_rgb=(255, 138, 132),
        logo_offset=(-100, -12),
    )
