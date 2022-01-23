from sdsRayanArvin.Dataset.ObjectData import ObjectData
from sdsRayanArvin.Request import Request


class Object:
    def __init__(self, requestClass: Request):
        self.Request = requestClass

    def ObjectByIdOrg(self) -> ObjectData:
        """
        get object data
        :return: :class:`Object <Object>` object
        """

        res = self.Request.sendWithToken('GET', 'object')
        objData = []

        for obj in res['Object']:
            objData.append(ObjectData(obj))

        return objData
