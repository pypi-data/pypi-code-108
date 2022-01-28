from portmgr import command_list, bcolors
import subprocess

def func(action):
    directory = action['directory']
    relative = action['relative']

    res = subprocess.call(
            ['docker-compose', 'build',
                '--pull',
                '--force-rm',
                '--compress'
            ]
    )

    if res != 0:
        print("Error building " + relative + "!")
        return res

    res = subprocess.call(['docker-compose', 'push'])

    if res != 0:
        print("Error pushing " + relative + "!")
        return res

    # res = subprocess.call(['docker', 'system', 'prune', '--all', '--force'])

    # if res != 0:
    #     print("Error pruning system!")
    #     return res

    return res

command_list['r'] = {
    'hlp': 'build, push to registry & remove image',
    'ord': 'nrm',
    'fnc': func
}
