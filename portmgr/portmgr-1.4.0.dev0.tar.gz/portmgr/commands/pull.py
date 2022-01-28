from portmgr import command_list, bcolors
import subprocess

def func(action):
    directory = action['directory']
    relative = action['relative']

    res = subprocess.call(["docker-compose", "pull"])

    if res != 0:
        print("Error pulling " + relative + "!")

    return 0

command_list['p'] = {
    'hlp': 'Pull image from repository',
    'ord': 'nrm',
    'fnc': func
}
