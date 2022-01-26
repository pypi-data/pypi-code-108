import os
import json

class data:
    

    # Read json and return dictionary
    def read_json(filename):
        with open (filename + '.json', 'r') as f:
            dic = json.load(f)
            return dic

    # create json file
    def create_json(filename):
        if os.path.exists(f'{filename}.json'):
            print('File already exist.')
        else:
            dic = {}
            with open(filename + '.json', 'a+') as f:
                json.dump(dic, f)

    # Add program to json file
    def add_json(filename, key, value):
        with open (filename + '.json', 'r+') as f:
            dic = json.load(f)
            dic = dic.copy()
            dic.update({key:value})
            f.seek(0)
            json.dump(dic, f, indent=2)

    # Remove program from json file
    def remove_element_json(filename, item_key):
        with open (filename + '.json') as f:
            dic = json.load(f)
            dic = dic.copy()
            if item_key not in dic:
                print(f'Program {item_key} not found')
            del dic[item_key]
            
        with open (filename + '.json', 'w') as f:
            json.dump(dic, f)


    #lst = read_json('data')
    #for _ in lst:
    #    print(_)