from portmgr import command_list
import subprocess


def func(action):
    relative = action['relative']

    res = subprocess.call(["docker-compose", "top"])

    if res != 0:
        print("Error listing processes of containers in " + relative + "!\n")

    return 0


command_list['t'] = {
    'hlp': 'List processes in containers',
    'ord': 'nrm',
    'fnc': func
}
