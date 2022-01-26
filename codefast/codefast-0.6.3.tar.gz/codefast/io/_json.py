import requests
import ast
import json
from codefast.logger import Logger
from codefast.io.file import FileIO


class FastJson:
    def __call__(self, file_name: str = '') -> dict:
        if file_name:
            if file_name.startswith('http'):
                return requests.get(file_name).json()
            return self.read(file_name)

    def read(self, path_or_str: str) -> dict:
        ''' read from string or local file, return a dict'''
        if len(path_or_str) < 255:
            try:
                return json.loads(open(path_or_str, 'r').read())
            except FileNotFoundError as e:
                Logger().warning("input is not a file, {}".format(e))

        try:
            return ast.literal_eval(path_or_str)
        except SyntaxError as e:
            Logger().error("input is not a valid json string, {}".format(e))

        return {}

    def write(self, d: dict, file_name: str):
        json.dump(d, open(file_name, 'w'), ensure_ascii=False, indent=2)

    def eval(self, file_name: str) -> dict:
        '''Helpful parsing single quoted dict'''
        return ast.literal_eval(FileIO.read(file_name, ''))

    def dumps(self, _dict: dict) -> str:
        '''Helpful parsing single quoted dict'''
        return json.dumps(_dict)
