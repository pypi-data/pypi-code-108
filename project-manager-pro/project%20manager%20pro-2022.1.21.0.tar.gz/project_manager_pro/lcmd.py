import json

from project_manager_pro._meta import cache_commands
from colorama import init, Style, Fore, Back

init(autoreset=True)


def _lcmd():
    file = open(cache_commands, 'r', encoding='utf-8')
    commands = json.load(file)

    if len(commands) == 0:
        print(Fore.RED + 'Commands not found')
    else:
        print(Fore.GREEN + 'Available commands:')

        for command in commands:
            alias = Style.BRIGHT + Fore.RED + command
            text = Style.RESET_ALL + Fore.CYAN + commands[command].replace('$', Style.BRIGHT + Fore.MAGENTA + '$')

            print('%-20s%-100s' % (alias, text))

