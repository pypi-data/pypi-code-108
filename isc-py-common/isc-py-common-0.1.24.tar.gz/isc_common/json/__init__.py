import json
import logging
from json import JSONDecodeError

from isc_common.string import StrToBytes, BytesToStr

logger = logging.getLogger(__name__)


def BytesToJson(mybytes):
    try:
        mystring = BytesToStr(mybytes)
        _json = json.loads(mystring)
        return _json
    except JSONDecodeError:
        return dict()


def JsonToBytes(myjson):
    mystring = json.dumps(myjson)
    bytes = StrToBytes(mystring)
    return bytes


def JsonToStr(myjson, indent=4, sort_keys=True):
    if isinstance(myjson, dict):
        if indent == 0:
            return json.dumps(myjson, indent=indent, sort_keys=sort_keys).replace('\n','')
        else:
            return json.dumps(myjson, indent=indent, sort_keys=sort_keys)
    else:
        raise Exception(f'{myjson} must by dict')


def StrToJson(mystring):
    if isinstance(mystring, str):
        try:
            return json.loads(mystring)
        except JSONDecodeError as ex:
            logger.error(ex)
            return dict()
    elif isinstance(mystring, dict):
        return mystring
    else:
        return dict()
