class styles:
    BOLD = "\u001b[1m"
    ITALIC = "\u001b[3m"
    UNDERLINE = "\u001b[4m"
    REVERSE = "\u001b[7m"
    HIDDEN = "\u001b[8m"
    OVERLINED = "\u001b[53m"
    RESET = "\033[0m"

def style(text=None, style=None, reset=True) -> str:
    """
    Style. Styling the font.
    -
    -----
    List :
    - `bold`
    - `italic` (Not widely supported)
    - `underline`
    - `reverse` (Swap foreground and background colors)
    - `hidden`
    - `overlined` (Not supported in Terminal app)
    """
    if style == "bold":
        if reset == False:
            styled = f"{styles.BOLD}{text}"
        else:
            styled = f"{styles.BOLD}{text}{styles.RESET}"

    elif style == "italic":
        if reset == False:
            styled = f"{styles.ITALIC}{text}"
        else:
            styled = f"{styles.ITALIC}{text}{styles.RESET}"

    elif style == "underline":
        if reset == False:
            styled = f"{styles.UNDERLINE}{text}"
        else:
            styled = f"{styles.UNDERLINE}{text}{styles.RESET}"

    elif style == "reverse":
        if reset == False:
            styled = f"{styles.REVERSE}{text}"
        else:
            styled = f"{styles.REVERSE}{text}{styles.RESET}"

    elif style == "hidden":
        if reset == False:
            styled = f"{styles.HIDDEN}{text}"
        else:
            styled = f"{styles.HIDDEN}{text}{styles.RESET}"

    elif style == "overlined":
        if reset == False:
            styled = f"{styles.OVERLINED}{text}"
        else:
            styled = f"{styles.OVERLINED}{text}{styles.RESET}"

    else:
        raise TypeError("Unknow style!")
    
    return styled
