def read(location):
    import json

    with open(location) as f:
        data = json.load(f)
    return data["data"],data["id"],data["name"]
def write(location,regdata):
    import json
    from datetime import datetime
    now = datetime.now()
    with open(location) as f:
        data = json.load(f)
    data["data"] = regdata
    data["last_modified"] = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(location, 'w') as outfile:
        json.dump(data, outfile)

def create(location,name,regdata):
    import json
    import random
    from datetime import datetime
    now = datetime.now()
    data = {}
    data["name"] = name
    data["data"] = regdata
    data["id"] = random.randint(100000000000,999999999999)
    data["data_created"] = now.strftime("%Y-%m-%d %H:%M:%S")
    data["last_modified"] = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(location, 'w') as outfile:
        json.dump(data, outfile)
    return data["id"]
class findfrom:
    def name(location,name):
        import json
        import os
        keys = []
        dir_list = os.listdir(location)
        for i in dir_list:
            if i.endswith(".json"):
                if location.endswith("/"):
                    i = location+i
                else:
                    i = location+"/"+i
                with open(i) as f:
                    data = json.load(f)
                if data["name"] == name:
                    keys.append(i)
        return keys
    def id(location,id):
        import json
        import os
        keys = []
        dir_list = os.listdir(location)
        for i in dir_list:
            if i.endswith(".json"):
                if location.endswith("/"):
                    i = location+i
                else:
                    i = location+"/"+i
                with open(i) as f:
                    data = json.load(f)
                if data["id"] == id:
                    keys.append(i)
        return keys
    def data(location,data):
        import json
        import os
        keys = []
        dir_list = os.listdir(location)
        for i in dir_list:
            if i.endswith(".json"):
                if location.endswith("/"):
                    i = location+i
                else:
                    i = location+"/"+i
                with open(i) as f:
                    data = json.load(f)
                if data["data"] == data:
                    keys.append(i)
        return keys
class get:
    def name(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["name"]
    def id(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["id"]
    def date_created(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["date_created"]
    def data(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["data"]
    def created(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["data_created"]
    def modified(location):
        import json
        import os
        with open(location) as f:
            data = json.load(f)
        return data["last_modified"]
                