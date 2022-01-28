from portmgr import command_list, bcolors
import subprocess
from compose.cli.command import get_project
from compose import project
from compose.project import OneOffFilter
from operator import attrgetter

def func(action):
    directory = action['directory']
    relative = action['relative']
    
    project = get_project('.')
    
    containers = sorted(
        project.containers(stopped=False) +
        project.containers(one_off=OneOffFilter.only, stopped=False),
        key=attrgetter('name'))
        
    names = []
    for container in containers:
      names.append(container.name)
      
    index = 0
    cont_count = len(names)
    if cont_count == 0:
      print("No containers found!")
      return 1
    elif cont_count > 1:
      i = 0
      for cont in names:
        print("(" + str(i) + ") " + cont)
        i += 1
      
      while True:
        choice = input("Choose container: ")
        if choice:
          try:
            index = int(choice)
            if index >= 0 and index < cont_count:
              break
          except ValueError:
            print("Please enter a number!")
            pass
        print("Please enter a number between 0 and " + cont_count - 1 + "!")
              
    container_id = names[index]
    print("Attaching to " + container_id)
    subprocess.call(["docker", "exec", "-it", container_id, "sh"])

    # res = subprocess.call(["docker-compose", "logs", "--follow", "--tail=200"])

    # if res != 0:
        # print("Error showing logs for " + relative + "!\n")

    return 0

command_list['a'] = {
    'hlp': 'Attach to process',
    'ord': 'nrm',
    'fnc': func
}
