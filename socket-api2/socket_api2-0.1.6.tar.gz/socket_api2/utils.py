import locale
import logging
import time

import colorama

colorama.init()

class SEND_METHOD:
    default_send = 0
    just_send = 1

def outstr(mode, text, start=""):
    """
    MODE = ["INFO", "DEBUG", "ERROR", "ACCESS"]
    """

    mode = mode.upper()

    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale()[0])    
    t = time.strftime('%Y.%m.%d %H:%M:%S')

    try:
        import colorama
        colorama.init()

        red = colorama.Fore.RED
        red2 = colorama.Fore.LIGHTRED_EX
        blue = colorama.Fore.BLUE
        blue2 = colorama.Fore.LIGHTBLUE_EX
        green = colorama.Fore.GREEN
        gray = colorama.Fore.LIGHTBLACK_EX
        gray2 = colorama.Fore.LIGHTWHITE_EX
        magenta = colorama.Fore.MAGENTA
        reset = colorama.Fore.RESET

        if mode.lower() == "info":
            print(f"{start}[{t}]{reset} {blue}<{mode}>{reset}: {blue2}{text}{reset}")
            logging.info(f"{start}[{t}] <{mode}>: {text}")

        elif mode.lower() == "debug":
            print(f"{start}[{t}]{reset} {gray}<{mode}>{reset}: {gray2}{text}{reset}")
            logging.debug(f"{start}[{t}] <{mode}>: {text}")


        elif mode.lower() == "error":
            print(f"{start}[{t}]{reset} {red}<{mode}>{reset}: {red2}{text}{reset}")
            logging.debug(f"{start}[{t}] <{mode}>: {text}")

        elif mode.lower() == "access":
            print(f"{start}[{t}]{reset} {green}<INFO>{reset}: {green}{text}{reset}")
            logging.info(f"{start}[{t}] <{mode}>: {text}")

        else:
            raise Exception(f"Wrong mode. Valid modes are INFO, DEBUG, ERROR, ACCESS not {mode}")

    except:
        if mode.lower() == "info":
            print(f"{start}[{t}] <{mode}>: {text}")
            logging.info(f"{start}[{t}] <{mode}>: {text}")

        elif mode.lower() == "debug":
            print(f"{start}[{t}] <{mode}>: {text}")
            logging.debug(f"{start}[{t}] <{mode}>: {text}")

        elif mode.lower() == "error":
            print(f"{start}[{t}] <{mode}>: {text}")
            logging.debug(f"{start}[{t}] <{mode}>: {text}")

        elif mode.lower() == "access":
            print(f"{start}[{t}] <INFO>: {text}")
            logging.info(f"{start}[{t}] <{mode}>: {text}")

        else:
            raise Exception(f"Wrong mode. Valid modes are INFO, DEBUG, ERROR, ACCESS not {mode}")
