import os
import subprocess

from .environment.environment import data
from .utils.utils import PATH, logo

CURRENT_PATH = PATH

class handle:
    
            
    def add(filename):
        name = input('Enter name of program to add this environment: ')
        path = input('Enter path of program executable: ')
        try:
            data.add_json(filename, name, path)
        except Exception as Error:
            print(Error)
            
    def build(filename, build):
        print(f'Launch file with name {build} will be created...')
        data.create_json(filename)
            
    def launch(filename, env):
        try:
            dic = data.read_json(filename)
            print(f'Launching workspace - {env}')
            logo()
            handle.run(dic)
        except FileNotFoundError:
            print(f'No Workspace named {env} found')
            handle.ls()
    
    def purge(filename, purge):
        if os.path.exists(filename):
            verify = input(f'Confirm to delete {purge} environment [y/n]: ')
            if verify == 'y':
                os.remove(filename)
        else:
            print(f'No environment named {purge}.')
            
    def remove_element(filename):
        item = input('Enter program name to delete from environment: ')
        data.remove_element_json(filename, item)
        
    def show_lst(filename, show_list):
        try:
            dic = data.read_json(filename)
            print(f'Workspace {show_list}')
            for _ in dic:
                print(f' {_}: {dic[_]}')
        except FileNotFoundError:
            print(f'No Workspace named {show_list} found')
            
    @staticmethod
    def ls():
        print('Here is list of available workspace:')
        for _ in os.listdir(CURRENT_PATH):
            if _.endswith('.json'):
                print(' ',_.replace('.json',''))
            
    @staticmethod                
    def run(dic):
        for _ in dic:
            try:
                subprocess.Popen(dic[_])
                print(f'Executed {_}')
            except Exception:
                print(f'Could not open {_}:{dic[_]}. Check if path/file_name is correct')