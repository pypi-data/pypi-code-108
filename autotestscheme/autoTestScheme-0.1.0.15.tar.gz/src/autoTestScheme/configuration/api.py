import os
from ..common import config, constant, logger


class Api(object):

    def __init__(self):
        self.api_data = {}

    def read_api_folder(self, *folder_name):
        if isinstance(folder_name, tuple) is False:
            folder_name = (folder_name,)
        folder = os.path.join(constant.BASE_DIR, *folder_name)
        for root, dirs, files in os.walk(folder):
            for name in files:
                _path = os.path.join(root, name)
                if name.endswith('.json') is True:
                    _data = config.Json(_path).get_object()
                    if _data.get('id') is not None:
                        self.register_api(_data)
                elif name.endswith('.proto') is True:
                    self.register_api(name[:-6], _path)

    def register_api(self, _data):
        _id = _data.get('id')
        if _id in list(self.api_data.keys()):
            logger.error("api({})重复注册".format(_id))
        self.api_data[_id] = _data

    def register_proto(self, _id, _path):
        if _id in list(self.api_data.keys()):
            logger.error("api({})重复注册".format(_id))
        self.api_data[_id] = _path

    def get_api(self, api_id):
        """
        返回api数据
        :param api_id:
        :return:
        """
        if api_id in list(self.api_data.keys()):
            return self.api_data[api_id]
        assert False, "api({})未注册".format(api_id)


