class colors:
    BLACK = "\033[40m"
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    PURPLE = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'
    # LIGHT COLORS
    GREY = '\033[100m'
    LRED = '\033[101m'
    LGREEN = '\033[102m'
    LYELLOW = '\033[103m'
    LBLUE = '\033[104m'
    LPURPLE = '\033[105m'
    LCYAN = '\033[106m'
    RESET = '\033[0m'

def bg(text, color, reset=True) -> str:
    """
    Backrounds. The color will appear behind the text.
    -
    -----
    Basic Colors :
    - `black`
    - `red`
    - `green`
    - `yellow`
    - `blue`
    - `purple`
    - `cyan`
    - `white`
    -----
    Light Colors :
    - `grey`
    - `lred`
    - `lgreen`
    - `lyellow`
    - `lblue`
    - `lpurple`
    - `lcyan`
    """

    if color == "black":
        if reset == False:
            colored = f"{colors.BLACK}{text}"
        else:
            colored = f"{colors.BLACK}{text}{colors.RESET}"

    elif color == "red":
        if reset == False:
            colored = f"{colors.RED}{text}"
        else:
            colored = f"{colors.RED}{text}{colors.RESET}"

    elif color == "green":
        if reset == False:
            colored = f"{colors.GREEN}{text}"
        else:
            colored = f"{colors.GREEN}{text}{colors.RESET}"

    elif color == "yellow":
        if reset == False:
            colored = f"{colors.YELLOW}{text}"
        else:
            colored = f"{colors.YELLOW}{text}{colors.RESET}"

    elif color == "blue":
        if reset == False:
            colored = f"{colors.BLUE}{text}"
        else:
            colored = f"{colors.BLUE}{text}{colors.RESET}"
    
    elif color == "purple":
        if reset == False:
            colored = f"{colors.PURPLE}{text}"
        else:
            colored = f"{colors.PURPLE}{text}{colors.RESET}"

    elif color == "cyan":
        if reset == False:
            colored = f"{colors.CYAN}{text}"
        else:
            colored = f"{colors.CYAN}{text}{colors.RESET}"
    
    elif color == "white":
        if reset == False:
            colored = f"{colors.WHITE}{text}"
        else:
            colored = f"{colors.WHITE}{text}{colors.RESET}"

    ### LIGHT COLORS            

    elif color == "grey":
        if reset == False:
            colored = f"{colors.GREY}{text}"
        else:
            colored = f"{colors.GREY}{text}{colors.RESET}"

    elif color == "lred":
        if reset == False:
            colored = f"{colors.LRED}{text}"
        else:
            colored = f"{colors.LRED}{text}{colors.RESET}"

    elif color == "lgreen":
        if reset == False:
            colored = f"{colors.LGREEN}{text}"
        else:
            colored = f"{colors.LGREEN}{text}{colors.RESET}"

    elif color == "lyellow":
        if reset == False:
            colored = f"{colors.LYELLOW}{text}"
        else:
            colored = f"{colors.LYELLOW}{text}{colors.RESET}"

    elif color == "lblue":
        if reset == False:
            colored = f"{colors.LBLUE}{text}"
        else:
            colored = f"{colors.LBLUE}{text}{colors.RESET}"
    
    elif color == "lpurple":
        if reset == False:
            colored = f"{colors.LPURPLE}{text}"
        else:
            colored = f"{colors.LPURPLE}{text}{colors.RESET}"

    elif color == "lcyan":
        if reset == False:
            colored = f"{colors.LCYAN}{text}"
        else:
            colored = f"{colors.LCYAN}{text}{colors.RESET}"

    else:
        raise TypeError("Unknow color!")

    return colored
