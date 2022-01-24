import json
from os import path
from utils.system.paths import Path
from utils.exceptions.Js_exception import badJSON


class JsHandler:
    def __init__(self, file_name):
        if isinstance(file_name, Path):
            self.file = file_name.path
        else:
            self.file = file_name

        if path.isfile(self.file):
            self.__loadFile()
        else:
            with open(self.file, 'w+') as f:
                json.dump({}, f, indent=4)

    def __loadFile(self) -> dict:
        fl = open(self.file, 'r+')
        return json.load(fl)

    def __dump(self, newDict):
        try:
            json.dumps(newDict)
        except Exception:
            raise badJSON('Unable to convert dictionary into JSON data')

        with open(self.file, 'w+') as file:
            json.dump(newDict, file, indent=4)

    def __getitem__(self, item):
        internal_json_dict = self.__loadFile()
        requestItem = internal_json_dict[item]
        return requestItem

    def __enter__(self):
        return self.__loadFile()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def update(self, updatedDict):
        Js = self.__loadFile()
        Js.update(updatedDict)
        self.__dump(Js)

    def getDict(self) -> dict:
        return self.__loadFile()

    def keys(self):
        return self.__loadFile().keys()

    def pop(self, key):
        Js = self.__loadFile()
        Js.pop(key)
        self.__dump(newDict=Js)
