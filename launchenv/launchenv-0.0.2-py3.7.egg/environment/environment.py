import json

class data:
    """Logic for launch file data """

    
    def read_json(filename):
        # Read json and return dictionary
        with open (filename + '.json', 'r') as f:
            dic = json.load(f)
            return dic

    
    def create_json(filename):
        # create json file
        dic = {}
        with open(filename + '.json', 'a+') as f:
            json.dump(dic, f)

    
    def add_json(filename, key, value):
        # Add program to json file
        with open (filename + '.json', 'r+') as f:
            dic = json.load(f)
            dic = dic.copy()
            dic.update({key:value})
            f.seek(0)
            json.dump(dic, f, indent=2)

    
    def remove_element_json(filename, item_key):
        # Remove program from json file
        with open (filename + '.json') as f:
            dic = json.load(f)
            dic = dic.copy()
            if item_key not in dic:
                print(f'Program {item_key} not found')
            del dic[item_key]
            
        with open (filename + '.json', 'w') as f:
            json.dump(dic, f)
