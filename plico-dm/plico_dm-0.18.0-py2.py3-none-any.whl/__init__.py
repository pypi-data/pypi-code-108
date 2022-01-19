from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus
from plico_dm.utils.constants import Constants


def _getDefaultConfigFilePath():
    from plico.utils.config_file_manager import ConfigFileManager
    cfgFileMgr= ConfigFileManager(Constants.APP_NAME,
                                  Constants.APP_AUTHOR,
                                  Constants.THIS_PACKAGE)
    return cfgFileMgr.getConfigFilePath()


defaultConfigFilePath= _getDefaultConfigFilePath()



def deformableMirror(hostname, port):

    from plico_dm.client.deformable_mirror_client import DeformableMirrorClient
    from plico.rpc.zmq_remote_procedure_call import ZmqRemoteProcedureCall
    from plico.rpc.zmq_ports import ZmqPorts
    from plico.rpc.sockets import Sockets


    rpc= ZmqRemoteProcedureCall()
    zmqPorts= ZmqPorts(hostname, port)
    sockets= Sockets(zmqPorts, rpc)
    return DeformableMirrorClient(rpc, sockets)
