class colors:
    BLACK = "\033[30m"
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    # LIGHT COLORS
    GREY = '\033[90m'
    LRED = '\033[91m'
    LGREEN = '\033[92m'
    LYELLOW = '\033[93m'
    LBLUE = '\033[94m'
    LPURPLE = '\033[95m'
    LCYAN = '\033[96m'
    RESET = '\033[0m'



def fore(text, color, reset=True) -> str:
    """
    Fore. The color will appear in the text.
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
