# -*- coding: utf-8 -*-
import locale
import datetime
import inspect
from alphalogic_api3.protocol import rpc_pb2
from alphalogic_api3.logger import log
from alphalogic_api3.exceptions import Exit


def value_type_field_definer(value_type):
    if str is value_type:
        return 'string_value'
    elif int is value_type:
        return 'long_value'
    elif float is value_type:
        return 'double_value'
    elif datetime.datetime is value_type:
        return 'datetime_value'
    elif bool is value_type:
        return 'bool_value'
    elif tuple is value_type:
        return 'tuple'
    elif list is value_type:
        return 'list'
    elif dict is value_type:
        return 'dict'
    else:
        raise Exception('Unknown type')


def create_command_definer(result_type):
    if str is result_type:
        return 'create_string_command'
    elif int is result_type:
        return 'create_long_command'
    elif float is result_type:
        return 'create_double_command'
    elif datetime.datetime is result_type:
        return 'create_datetime_command'
    elif bool is result_type:
        return 'create_bool_command'
    elif list is result_type or dict is result_type:
        return 'create_map_command'
    else:
        raise Exception('Unknown type')


def create_parameter_definer(result_type):
    if str is result_type:
        return 'create_string_parameter'
    elif int is result_type:
        return 'create_long_parameter'
    elif float is result_type:
        return 'create_double_parameter'
    elif datetime.datetime is result_type:
        return 'create_datetime_parameter'
    elif bool is result_type:
        return 'create_bool_parameter'
    elif list is result_type or dict is result_type:
        return 'create_map_parameter'
    else:
        raise Exception('Unknown type')


def get_command_argument_type(arg):
    if type(arg) == tuple:
        for val_type in arg:
            if type(val_type) == dict:
                val_dict = val_type.values()[0]
                return type(val_dict)
            else:
                return type(val_type)
    else:
        return type(arg)


def decode_string(s):
    """
    todo remove
    """
    return s


def epoch():
    return datetime.datetime.utcfromtimestamp(0)


def milliseconds_from_epoch(dt):
    return int((dt - epoch()).total_seconds() * 1000)


def create_map_value(value_rpc, value):
    for key, x in value.items():
        value_type = type(x)
        value_into = value_rpc.dict_value.value[key]
        build_rpc_value(value_into, value_type, x)


def create_list_value(value_rpc, value):
    for x in value:
        value_type = type(x)
        value_into = value_rpc.list_value.value.add()
        build_rpc_value(value_into, value_type, x)


def build_rpc_value(value_rpc, value_type, value=None):
    if value_type == int:
        value_rpc.long_value = value if value else 0
    elif value_type == float:
        value_rpc.double_value = value if value else 0.0
    elif value_type == datetime.datetime:
        if value:
            value_rpc.datetime_value = int((value - datetime.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()) * 1000 \
                                       + int(value.microsecond / 1000)
        else:
            value_rpc.datetime_value = 0
    elif value_type == bool:
        value_rpc.bool_value = value if value else False
    elif value_type == str:
        value_rpc.string_value = value if value else ''
    elif value_type == list:
        if value:
            map(lambda x: build_rpc_value(value_rpc.list_value.value.add(), type(x), x),
                list(filter(lambda x: x is not None, value)))
        else:
            value_rpc.list_value.value.extend([])
    elif value_type == dict:
        if value:
            list(map(lambda item: build_rpc_value(value_rpc.dict_value.value[item[0]], type(item[1]), item[1]),
                list(filter(lambda item: item[0] is not None and item[1] is not None, value.items()))))
        else:
            value_rpc.dict_value.value['a'].long_value = 1
            del value_rpc.dict_value.value['a']

    elif value_type == str:
        raise Exception('\'str\' type using is prohibited')


def get_rpc_value(value_type, value=None):
    value_rpc = rpc_pb2.Value()
    build_rpc_value(value_rpc, value_type, value)
    return value_rpc


def value_from_rpc(value_rpc):
    if value_rpc.HasField('bool_value'):
        return value_rpc.bool_value
    elif value_rpc.HasField('long_value'):
        return value_rpc.long_value
    elif value_rpc.HasField('double_value'):
        return value_rpc.double_value
    elif value_rpc.HasField('datetime_value'):
        return datetime.datetime.utcfromtimestamp(value_rpc.datetime_value / 1000) \
               + datetime.timedelta(milliseconds=value_rpc.datetime_value % 1000)
    elif value_rpc.HasField('string_value'):
        return value_rpc.string_value
    elif value_rpc.HasField('list_value'):
        l = []
        list(map(lambda x: l.append(value_from_rpc(x)), value_rpc.list_value.value))
        return l
    elif value_rpc.HasField('dict_value'):
        d = dict()
        list(map(lambda x:  d.update({x[0]: value_from_rpc(x[1])}), value_rpc.dict_value.value.items()))
        return d


def shutdown(signum, frame):
    log.info("Shutdown. Signal is {0}".format(signum))
    raise Exit


def get_class_name_from_str(class_name_str):
    frame = inspect.currentframe()
    while frame:
        if class_name_str in frame.f_locals:
            return frame.f_locals[class_name_str]
        frame = frame.f_back

    log.warn('{0} is not a class of device.'.format(class_name_str))

    #raise Exception('{0} is not a class of device'.format(class_name_str))