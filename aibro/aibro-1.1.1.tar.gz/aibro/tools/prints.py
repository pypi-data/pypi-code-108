from colorama import Fore
from colorama import Style


def print_sending(msg: str):
    print(f"[SENDING]: {msg}")


def print_receiving(msg: str):
    print(f"[RECEIVING]: {msg}")


def print_launching(msg: str):
    print(f"[LAUNCHING]: {msg}")


def print_gearing(msg: str):
    print(f"[GEARING]: {msg}")


def print_success(msg: str):
    print(f"[SUCCESS]: {msg}")


def print_err(msg: str):
    print(Fore.RED + f"[ERROR]: {msg}")
    print(Style.RESET_ALL)


def print_warning(msg: str):
    print(Fore.YELLOW + f"[WARNING]: {msg}")
    print(Style.RESET_ALL)


def print_highlight(msg: str):
    print(Fore.GREEN + f"{msg}")
    print(Style.RESET_ALL)
