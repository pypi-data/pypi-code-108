from typing import Dict, Set, List

from centaur._.pyvmps.client.constants import PayloadKey
from centaur._.pyvmps.cfg.config import MessageType, PyvmpProtocol


def construct_res_err_message(err: Dict) -> Dict:
    return {PyvmpProtocol.MSG_TYPE: MessageType.RESP_ERR.value, PyvmpProtocol.DATA: err}


def construct_res_ok_message(data: str, res_attrs: Dict = None) -> Dict:
    if res_attrs:
        return {
            PyvmpProtocol.MSG_TYPE: MessageType.RESP_OK.value,
            PyvmpProtocol.DATA: data,
            PyvmpProtocol.RES_ATTRS: res_attrs,
        }
    return {PyvmpProtocol.MSG_TYPE: MessageType.RESP_OK.value, PyvmpProtocol.DATA: data}


def construct_reg_msg(attrs: Dict):
    return {PyvmpProtocol.MSG_TYPE: MessageType.VMP_STARTUP_SUCCEEDED.value, PyvmpProtocol.VMP_STARTUP_OK_ATTRS: attrs}


def construct_err_reg_msg(err_attrs: Dict, err_msg: Dict):
    return {
        PyvmpProtocol.MSG_TYPE: MessageType.VMP_STARTUP_ERR.value,
        PyvmpProtocol.DATA: err_msg,
        PyvmpProtocol.VMP_STARTUP_ERR_ATTRS: err_attrs,
    }


def unpack_and_check_verb(data: Dict, verb_list: Set):
    usr_data = data.get(PayloadKey.USR_DATA)
    if not usr_data:
        raise Exception("No usr data")
    verb = data.get(PayloadKey.VERB)
    if not verb or verb not in verb_list:
        raise Exception(f"{verb} not supported by model")
    return usr_data, verb
