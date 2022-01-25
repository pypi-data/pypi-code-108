"""create bars that fill a given ration of horizontal space with symbols."""

styles = {
    "simple": (" ", "█"),
    "blocks": (" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"),
    "clocks": (
        " ",
        "🕛",
        "🕧",
        "🕐",
        "🕜",
        "🕑",
        "🕝",
        "🕒",
        "🕞",
        "🕓",
        "🕟",
        "🕔",
        "🕠",
        "🕕",
        "🕡",
        "🕖",
        "🕢",
        "🕗",
        "🕣",
        "🕘",
        "🕤",
        "🕙",
        "🕥",
        "🕚",
        "🕦",
        "█",
    ),
    "shade": (" ", "░", "▒", "▓", "█"),
    "blocks_fall": (" ", "▔", "🮂", "🮃", "▀", "🮄", "🮅", "🮆", "█"),
    "blocks_rise": (" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"),
    "domino": tuple([" "] + [chr(x) for x in range(127075, 127124)] + ["█"]),
    "diagonal": (" ", "🬼", "🬽", "🬾", "🬿", "🭀", "🭑", "🭐", "🭏", "🭎", "🭍", "🭌", "█"),
    "diagonal_var": (" ", "🭗", "🭘", "🭙", "🭚", "🭛", "🭜", "🭡", "🭠", "🭟", "🭞", "🭝", "█"),
    "dots": (" ", "·", "⁚", "⁖", "⁘", "⁙"),
    "line": (" ", "╴", "―"),
    "dotted_line": (" ", "·", "⋯"),
    "mid": (" ", "⠂", "⠒"),
    "diamonds": (" ", "🮠", "🮡", "🮣", "🮢", "🮧", "🮥", "🮦", "🮤", "🮬", "🮪", "🮫", "🮭", "🮮"),

}


def bar(fraction: float, total: int, style="blocks") -> str:
    """return a string containing a bar of the fraction ([0.0, 1.0])
    of the total width using unicode block characters"""

    blocks = styles[style]
    blocks_to_fill = total * fraction
    n_blocks = len(blocks)
    residual = (blocks_to_fill - int(blocks_to_fill)) * n_blocks
    if int(residual) == 0 and fraction > 0.0 and int(blocks_to_fill) == 0:
        residual = 1
    result = blocks[-1] * int(blocks_to_fill)
    if fraction < 1.0:
        result += blocks[int(residual)]
    return result.strip()


if __name__ == "__main__":

    import sys
    from time import sleep

    # switch off blinking cursor
    sys.stdout.write("\x1b[?25l")

    t = 10
    w = 10
    for style, blocks in styles.items():
        n_blocks = len(blocks)
        for i in range(w * n_blocks):
            print(
                "\r" + f"{style:<20}" + "\t" + bar(i / (w * n_blocks), w, style),
                end="",
            )
            sleep(t / (w * n_blocks))
        print()
