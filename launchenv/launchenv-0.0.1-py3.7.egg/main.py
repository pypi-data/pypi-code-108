import os
import argparse

from .launch import handle
from .utils.utils import PATH


CURRENT_PATH = PATH

# Initalise function to call other functions based on arguments
def initalise(build=None, add=None, show_list=None, remove=None, purge=None, env=None, ls=False):
    
    # Create new work environment
    if build:
        filename = f'{CURRENT_PATH}\{build}'
        handle.build(filename, build)
    
    # Add program to existing work environment
    if add:
        filename = f'{CURRENT_PATH}\{add}'
        handle.add(filename)
        
    # Show all programs in the environment
    if show_list:
        filename = f'{CURRENT_PATH}\{show_list}'
        handle.show_lst(filename, show_list)
        
    # Delete program from given environment
    if remove:
        filename = f'{CURRENT_PATH}\{remove}'
        handle.remove_element(filename)
        
    # Remove the work environment
    if purge:
        filename = f'{CURRENT_PATH}\{purge}' + '.json'
        handle.purge(filename, purge)
    
    # Run environment
    if env:
        filename = f'{CURRENT_PATH}\{env}'
        handle.launch(filename, env)
        
    if ls:
        handle.ls()
        
def main():
    # Parser arguments
    parser = argparse.ArgumentParser(description='Run environment')
    parser.add_argument('-build', '--build', help='Create new work environment/workspace', 
                         type=str, metavar='')
    parser.add_argument('-a', '--add', help='Add program to existing work environment', 
                        type=str, metavar='')
    parser.add_argument('-s', '--show', help='Show all program in given work environment', 
                        type=str, metavar='')
    parser.add_argument('-remove', '--remove', help='Remove program from given work environment', 
                        type=str, metavar='')
    parser.add_argument('-purge', '--purge', help='delete the work environment file', 
                        type=str, metavar='')
    parser.add_argument('-env', '--env', help='Run environment', 
                        type=str, metavar='')
    parser.add_argument('-ls', '--list', help='List all available work environments', 
                        action='store_true')
    args = parser.parse_args()
    
    initalise(build=args.build, add=args.add, 
              show_list=args.show, remove=args.remove, 
              purge=args.purge, env=args.env , ls=args.list)
    
    
if __name__ == '__main__':
    main()