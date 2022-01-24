import os
import logging
import time
import yaml
import glob

def user_select_contentPack():
    """
    This function is list out content packs and allow the end user to select from the listed options.
    """
    path = './contentpacks'
    directory_contents = os.listdir(path)
    for item in directory_contents:
        if item != 'archive':
            print('Content Pack: '+item)
    contentPack_selection = input('Please enter the name of the Content Pack from the above list: ')
    if contentPack_selection not in directory_contents:
        print('Please verify you have the content pack folder name correct and run the script again selection and try again')
        exit()
    # Set ENV for Classes
    os.environ["CONTENTPACK"] = contentPack_selection
    path_to_contentPack = os.path.join('contentpacks', contentPack_selection)
    print('Current files in: '+contentPack_selection)
    files = glob.glob(path_to_contentPack+'/*')
    for file in files: print(file)
    print('Reading version.yaml')
    time.sleep(1)
    version_config = open(os.path.join('./', 'contentpacks', contentPack_selection, 'version.yaml'))
    parsed_version_config = yaml.load(version_config, Loader=yaml.FullLoader)
    print('###############################')
    print('')
    print('Verify the info below before continuing')
    print('Title: '+parsed_version_config['title'])
    print('Content Pack Version: '+parsed_version_config['version'])
    print('Description: '+parsed_version_config['description'])
    print('')
    print('###############################')
    return path_to_contentPack