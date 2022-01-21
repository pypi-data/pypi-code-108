import json

from project_manager_pro._meta import cache_commands
from colorama import init, Style, Fore, Back

init(autoreset=True)


def _acmd(alias, body):
    file = open(cache_commands, 'r', encoding='utf-8')
    commands = json.load(file)

    commands[alias] = body

    print(Fore.GREEN + '' + alias + ' \"' + commands[alias] + '\"' + ' command added')

    with open(cache_commands, 'w', encoding='utf-8') as f:
        f.write(json.dumps(commands, ensure_ascii=False))
