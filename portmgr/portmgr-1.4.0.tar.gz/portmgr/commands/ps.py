from portmgr import command_list, bcolors
import subprocess

def func(action):
    directory = action['directory']
    relative = action['relative']

    res = subprocess.call(["docker-compose", "ps"])

    if res != 0:
        print("Error listing containers for " + relative + "!\n")

    return 0

command_list['c'] = {
    'hlp': 'List containers',
    'ord': 'nrm',
    'fnc': func
}
