from portmgr import command_list, bcolors
import subprocess

def func(action):
    directory = action['directory']
    relative = action['relative']

    res = subprocess.call(
            ['docker-compose', 'build', '--pull'],
            env={
                'COMPOSE_DOCKER_CLI_BUILD': '1',
                'DOCKER_BUILDKIT': '1'
                },
            )

    if res != 0:
        print("Error building " + relative + "!")

    return res

command_list['b'] = {
    'hlp': 'Build local image',
    'ord': 'nrm',
    'fnc': func
}
