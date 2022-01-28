from portmgr import command_list, bcolors
import subprocess

def func(action):
    directory = action['directory']
    relative = action['relative']

    res = subprocess.call(["docker-compose", "up", "-d"])
    # p = subprocess.Popen(["docker-compose", "up", "-d"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # out, err = p.communicate()

    # if out != "":
       # print(out.decode("UTF-8"))

    if res != 0:
        print("Error creating " + relative + "!")
    
    # print(bcolors.FAIL + err.decode("UTF-8") + bcolors.ENDC)

    return 0

command_list['u'] = {
    'hlp': 'Create container',
    'ord': 'nrm',
    'fnc': func
}
