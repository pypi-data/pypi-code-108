import random
import os
import platform
from time import sleep

class clear:
    def __init__(self, delay:int=None):
        if platform.uname()[0] == "Windows":
            if delay == None:
                pass
            else:
                sleep(delay)
            os.system("cls")
            
        else:
            if delay == None:
                pass
            else:
                sleep(delay)
            os.system("clear")

fore_color_list = [
    '\033[31m',
    '\033[32m',
    '\033[33m',
    '\033[34m',
    '\033[35m',
    '\033[36m',
    '\033[37m',
    '\033[90m',
    '\033[91m',
    '\033[92m',
    '\033[93m',
    '\033[94m',
    '\033[95m',
    '\033[96m'
]

bg_color_list = [
    '\033[41m',
    '\033[42m',
    '\033[43m',
    '\033[44m',
    '\033[45m',
    '\033[46m',
    '\033[47m',
    '\033[100m',
    '\033[101m',
    '\033[102m',
    '\033[103m',
    '\033[104m',
    '\033[105m',
    '\033[106m'
]

class blink:
    """
    Blink is class to make blinking text.
    Warning : You don't need to use print! it's already inside every blink function.
    -----
    Classmethod :
    - `fore` | for blinking Fore
    - `bg` | for blinking Backgrounds
    """
    
    @classmethod
    def fore(self, text:str, loop:int=20):
        """
        Blinking fore. No return
        Warning : You don't need to use print! it's already inside every blink function.
        -----
        Parameters :
        - text: `str`
        - loop: `int` | Default: `20`
        """
        for i in range(loop):
            random_color = random.choice(fore_color_list)
            clear(delay=0.1)
            colored = f"{random_color}{text}\033[0m"
            print(colored)

    
    @classmethod
    def bg(self, text:str, loop:int=20):
        """
        Blinking backgrounds. No return.
        Warning : You don't need to use print! it's already inside every blink function.
        -----
        Parameters :
        - text: `str`
        - loop: `int` | Default: `20`
        """
        for i in range(loop):
            random_color = random.choice(bg_color_list)
            clear(delay=0.1)
            colored = f"{random_color}{text}\033[0m"
            print(colored)
