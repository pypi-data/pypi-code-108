import json

from project_manager_pro._meta import cache_commands
from colorama import init, Style, Fore, Back

init(autoreset=True)


def _dcmd(alias):
    file = open(cache_commands, 'r', encoding='utf-8')
    commands = json.load(file)

    if alias in commands:
        print(Fore.GREEN + 'Command ' + alias + ' \"' + commands[alias] + '\"' + ' has been deleted')
        commands.pop(alias)
    else:
        print(Fore.RED + 'Command \'' + alias + '\' not found')

    with open(cache_commands, 'w', encoding='utf-8') as f:
        f.write(json.dumps(commands, ensure_ascii=False))
