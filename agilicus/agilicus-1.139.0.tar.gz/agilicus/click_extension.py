import json
from click.types import File


class JSONFile(File):
    def convert(self, value, param, ctx):
        file_obj = super().convert(value, param, ctx)
        file = json.loads(file_obj.read())
        return file
