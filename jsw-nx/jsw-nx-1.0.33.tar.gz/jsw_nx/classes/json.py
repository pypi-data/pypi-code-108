import json


class JSON:
    @classmethod
    def stringify(cls, data, **opts):
        return json.dumps(data, **opts)

    @classmethod
    def parse(cls, data):
        return json.loads(data)
