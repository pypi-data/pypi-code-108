from sdsRayanArvin.Dataset.ObjectData import ObjectData
from sdsRayanArvin.Request import Request
from sdsRayanArvin.Repository import Repository


class Object(Repository):
    def ObjectByIdOrg(self):
        res = self.Request.sendWithToken('GET', 'object_all')
        try:
            return ObjectData(res['Object']).data
        except:
            return []
