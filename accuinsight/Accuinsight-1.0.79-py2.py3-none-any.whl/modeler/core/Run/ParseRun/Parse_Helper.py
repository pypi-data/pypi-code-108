from Accuinsight.modeler.core.LcConst.LcConst import RUN_OBJ_DATA_VERSION
from Accuinsight.modeler.protos.life_cycle_pb2 import LcParam


def get_data_version(param_data):
    data_version = ''
    if RUN_OBJ_DATA_VERSION in param_data:
        data_version = param_data[RUN_OBJ_DATA_VERSION]

    return LcParam(
        key=RUN_OBJ_DATA_VERSION,
        value=data_version
    )
