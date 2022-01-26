from exectools.tools_excel import ExecExcel
from exectools.tools_basic import Tools
from json import load, dump


class ExecImport:
    def __init__(self, path):
        self.path = Tools.extend_path(path)

    def from_json(self):
        with open(self.path, 'r') as f:
            return load(f)

    def from_excel(self, sheet='Sheet1', nana=None, orient='records', empty=False) -> iter:
        return ExecExcel(self.path, sheet, nana).read(orient, empty)


class ExecExport:
    def __init__(self, path='~/Desktop/'):
        self.path = Tools.extend_path(path)

    def to_json(self, data, filename):
        with open(self.path+f'{filename}.json', 'w') as f:
            dump(data, f)

    def to_excel(self, data: list, filename, sheet='Sheet1', nana=None):
        ExecExcel(self.path, sheet, nana).write(data, filename)
