

from fakts.grants.base import FaktsGrant
import yaml


class YamlGrant(FaktsGrant):

    def __init__(self, filepath = "random.yaml") -> None:
        super().__init__()
        self.filepath = filepath


    async def aload(self, previous = {}, **kwargs):
        with open(self.filepath,"r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)

        return config
