from portmgr import command_list
import subprocess
import json
from compose.cli.command import get_project
from compose.project import OneOffFilter
from compose import project
from operator import attrgetter

def func(action):
    directory = action['directory']
    relative = action['relative']

    project = get_project('.')

    containers = sorted(
        project.containers() +
        project.containers(one_off=OneOffFilter.only, stopped=False),
        key=attrgetter('name'))

    names = []
    res = 0
    for container in containers:
      repo_digests = container.image_config['RepoDigests']
      if repo_digests:
          image_name = repo_digests[0]
      else:
          repo_digests = container.image_config['RepoTags']
      if repo_digests:
          image_name = repo_digests[0]
      else:
          continue

      print(f'Scanning {image_name} of {container.service}')
      scan_res = subprocess.run(['trivy', '-q', 'image', '-s', 'CRITICAL', '--exit-code', '1', image_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
      if scan_res.returncode != 0:
        print('Found vulnerabilites:')
        print(scan_res.stdout)
        res = scan_res.returncode

      #print("Name: %s" % container.name)
      #names.append(container.name)
      #config_str = subprocess.check_output(["docker", "inspect", "-f", '{{json .}}', container.id], stdout=subprocess.PIPE)
      #json.loads(config_str)
      #print("IP: %s" % ip)
      #print(container.inspect)


    #ID = subprocess.run(["docker-compose", "ps", '-q'], stdout=subprocess.PIPE).stdout

    #if res != 0:
    #    print("Error listing containers for " + relative + "!\n")

    return res

command_list['v'] = {
    'hlp': 'Scan container images for vulnerabilities',
    'ord': 'nrm',
    'fnc': func
}
