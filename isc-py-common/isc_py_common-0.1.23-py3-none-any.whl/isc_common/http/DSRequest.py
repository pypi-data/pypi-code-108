import logging

from isc_common import setAttr, delAttr, Wrapper, delAttr1
from isc_common.http.RPCRequest import RPCRequest
from isc_common.json import BytesToJson

logger = logging.getLogger(__name__)


class RequestData:
    def __init__(self, _dict = None, request = None):
        if request:
            self.__data_dict__ = request.get_data()
        elif _dict:
            self.__data_dict__ = _dict
        else:
            self.__data_dict__ = dict()
        super()

    def getDataOfKey(self, key, default = None):
        return self.__data_dict__.get(key, default)

    def update(self, key, value):
        self.__data_dict__.update((key, value))
        return RequestData(self.__data_dict__)

    def getDataWithOutField(self, list_fields):
        if isinstance(list_fields, list):
            return RequestData({key: self.__data_dict__[key] for key in self.__data_dict__ if not key in list_fields})
        else:
            return RequestData(self.__data_dict__)

    def getDataNotContain(self, *sub_strs):
        res = RequestData()
        for sub in sub_strs:
            self.__data_dict__ = {key: self.__data_dict__[key] for key in self.__data_dict__ if not str(key).__contains__(sub)}
        return RequestData(self.__data_dict__)

    def dict(self):
        return self.__data_dict__


class DSRequest(RPCRequest):
    alive_only = None
    begdate = None
    dataPageSize = 75
    drawAheadRatio = 1.2
    enabledAll = None
    endRow = None
    enddate = None
    httpHeaders = None
    json = None
    startRow = None
    tag = None
    transaction = None
    visibleMode = 'none'

    _user = None

    @property
    def user(self):
        from isc_common.auth.models.user import User
        if self._user is None:
            if self.httpHeaders is not None and self.httpHeaders.USER_ID:
                self._user = User.objects.get(id = self.httpHeaders.USER_ID)
                return self._user
            else:
                if self.transaction is not None:
                    operations = self.transaction.operations
                    if isinstance(operations, list):
                        for operation in operations:
                            data = operation.data
                            if data.httpHeaders is not None and data.httpHeaders.USER_ID is not None:
                                self._user = User.objects.get(id = data.httpHeaders.USER_ID)
                                return self._user

                # raise Exception('user not enable type')
        return self._user

    @property
    def user_id(self):
        return self.user.id

    @property
    def fio(self):
        return self.user.get_short_name

    @property
    def username(self):
        return self.user.username

    @property
    def is_admin(self):
        return self.user.is_admin

    @property
    def is_develop(self):
        return self.user.is_develop

    def set_user_data(self, user):
        from isc_common.auth.models.user import User
        from isc_common.number import ToInt

        _user = ToInt(user)
        if isinstance(_user, int):
            self._user = User.objects.get(id = _user)
        elif isinstance(user, str):
            self._user = User.objects.get(username = user)
        else:
            raise Exception('user not enable type')

    def __init__(self, request, **kwargs):
        if request is not None and request.method == "POST" and request.body != b'':
            self.json = BytesToJson(request.body)
            if isinstance(self.json, dict) and len(self.json) > 0:
                data = self.json.get('data')
                if isinstance(data, dict):
                    httpHeaders = data.get('httpHeaders')
                    if isinstance(httpHeaders, dict):

                        if httpHeaders.get('WS_CHANNEL') is not None:
                            self.ws_channel = httpHeaders.get('WS_CHANNEL')

                        if httpHeaders.get('WS_PORT') is not None:
                            self.ws_port = httpHeaders.get('WS_PORT')

                        if httpHeaders.get('HOST') is not None:
                            self.host = httpHeaders.get('HOST')

                        if httpHeaders.get('USERNAME') is not None:
                            self.set_user_data(user = httpHeaders.get('USERNAME'))

                        if httpHeaders.get('USER_ID') is not None:
                            self.set_user_data(user = httpHeaders.get('USER_ID'))

                        delAttr(self.json.get('data'), 'httpHeaders')
                    else:
                        if data.get('user_id') is not None:
                            self.set_user_data(user = data.get('user_id'))
                else:
                    login = self.json.get('login')
                    if login is not None:
                        self.set_user_data(user = login)
                    else:
                        httpHeaders = self.json.get('httpHeaders')
                        if httpHeaders is not None:
                            self.set_user_data(user = httpHeaders.get('USER_ID'))

        elif request.method == "GET":
            get_dict = dict(request.GET)
            self.json = get_dict

            if not self.json:
                self.json = delAttr1(kwargs, "asnc")

            ws_channel = get_dict.get('ws_channel')
            if isinstance(ws_channel, list) and len(ws_channel) > 0:
                self.ws_channel = ws_channel[0]

            port = get_dict.get('port')
            if isinstance(port, list) and len(port) > 0:
                self.ws_port = port[0]

            host = get_dict.get('host')
            if isinstance(host, list) and len(host) > 0:
                self.host = host[0]

            user_id = get_dict.get('user_id')
            if isinstance(user_id, list) and len(user_id) > 0:
                self.set_user_data(user = user_id[0])

        RPCRequest.__init__(self, self.json)

    def delete_underscore_element(self, data):
        if not isinstance(data, dict):
            raise Exception('data must be dict')

        res = dict()
        for key, value in data.items():
            if str(key).find('_', 0, 1) == -1:
                setAttr(res, key, value)
        return res

    def get_data(self, excluded_keys = ['grid']):
        res = None
        if isinstance(self.json, dict):
            data = self.json.get('data')
            if isinstance(data, dict):
                res = data
            elif isinstance(data, str):
                return data
            else:
                res = self.json

            # res = dict((key, value) for (key, value) in res.items() if not key.startswith('_')  and key not in excluded_keys)
            res = dict((key, value) for (key, value) in res.items() if key not in excluded_keys)
        # return self.delete_underscore_element(res)
        return res

    def get_data_wrapped(self, excluded_keys = ['grid'], cls = Wrapper):
        return cls(**self.get_data(excluded_keys = excluded_keys))

    def get_old_data(self, excluded_keys = ['grid']):
        res = None
        if isinstance(self.json, dict):
            data = self.json.get('oldValues')
            if isinstance(data, dict):
                res = data
            elif isinstance(data, str):
                return data
            else:
                res = self.json

            res = dict((key, value) for (key, value) in res.items() if not key.startswith('_') and key not in excluded_keys)
        # return self.delete_underscore_element(res)
        return res

    def get_old_data_wrapped(self, excluded_keys = ['grid'], cls = Wrapper):
        return cls(**self.get_old_data(excluded_keys = excluded_keys))

    def get_all_data(self, excluded_keys = ['grid']):
        res = None
        if isinstance(self.json, dict):
            data = self.json.get('data')
            if isinstance(data, dict):
                res = data
            elif isinstance(data, str):
                return data
            else:
                res = self.json

        return res

    def set_data(self, data):
        if isinstance(data, dict):
            setAttr(self.json, 'data', data)
        else:
            delAttr(self.json, 'data')

    def update_data(self, data):
        if isinstance(data, dict):
            self.json.update(data)

    def set_sort_by(self, sort_by):
        if not isinstance(sort_by, list):
            sort_by = [sort_by]

        setAttr(self.json, 'sortBy', sort_by)

    def set_criteria(self, criteria, excluded_keys = ['grid']):
        data = self.get_all_data(excluded_keys = excluded_keys)
        if isinstance(data, dict):
            setAttr(data, 'criteria', criteria)
        else:
            delAttr(data, 'criteria')

    def get_criteria(self, excluded_keys = ['grid']):
        data = self.get_data(excluded_keys = excluded_keys)
        if isinstance(data, dict):
            criteria = data.get('criteria')
        else:
            return dict()

        if isinstance(criteria, list):
            return criteria
        else:
            return []

    def get_data_array(self, excluded_keys = ['grid']):
        res = None
        if isinstance(self.json, dict):
            transaction = self.json.get('transaction')
            if transaction:
                operations = transaction.get('operations')
            else:
                return (False, [self.get_data()])

            res = (True, [dict((key, value) for (key, value) in operation.items() if not str(key).startswith('_') and key not in excluded_keys) for operation in operations])
            # res = (True, [dict((key, value) for (key, value) in operation.items() if value is not None and not str(key).startswith('_') and key not in excluded_keys) for operation in operations])
        return res

    def get_oldValues(self, excluded_keys = ['grid']):
        res = None
        if isinstance(self.json, dict):
            if self.json.get('oldValues', None) and isinstance(self.json.get('oldValues', None), dict):
                res = self.json.get('oldValues')
            else:
                res = self.json

            res = dict((key, value) for (key, value) in res.items() if not str(key).startswith('_') and key not in excluded_keys)
            # res = dict((key, value) for (key, value) in res.items() if value is not None and not str(key).startswith('_') and key not in excluded_keys)
        return res

    def get_id(self):
        return self.get_data().get('id', self.get_oldValues().get('id'))

    def get_operationtype(self):
        return self.json.get('operationType')

    def get_username(self):
        return self.get_data().get('username')

    def get_ids(self, field_name = 'id'):
        multi, data_array = self.get_data_array()
        if data_array:
            if multi:
                ids = [record.get('data').get(field_name) for record in data_array]
            else:
                ids = [record.get('data').get(field_name) if record.get('data') else record.get(field_name) for record in data_array]
        else:
            ids = [0]
        return [id for id in ids if id is not None]

    def get_tuple_ids(self, field_name = 'id'):
        multi, data_array = self.get_data_array()
        if data_array:
            if multi:
                ids = [(record.get('data').get(field_name), record.get('visibleMode', 'none')) for record in data_array]
            else:
                ids = [(record.get('data').get(field_name), self.visibleMode) if record.get('data') else (record.get(field_name), self.visibleMode) for record in data_array]
        else:
            ids = [(0, "none")]
        return ids

    def get_olds_tuple_ids(self, field_name = 'id'):
        multi, data_array = self.get_data_array()
        if data_array:
            if multi:
                ids = [(record.get('oldValues').get(field_name), record.get('visibleMode', 'none')) for record in data_array]
            else:
                ids = [(record.get('oldValues').get(field_name), self.visibleMode) if record.get('data') else (record.get(field_name), self.visibleMode) for record in data_array]
        else:
            ids = [(0, "none")]
        return ids

    def get_old_ids(self, field_name = 'id'):
        multi, data_array = self.get_data_array()
        if data_array:
            if multi:
                ids = [record.get('oldValues').get(field_name) for record in data_array]
            else:
                ids = [record.get('oldValues').get(field_name) if record.get('oldValues') else record.get(field_name) for record in data_array]
        else:
            ids = [0]
        return [id for id in ids if id is not None]

    def __str__(self):
        return str(self.__dict__)
