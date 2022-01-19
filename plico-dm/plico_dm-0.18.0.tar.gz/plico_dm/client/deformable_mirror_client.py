#!/usr/bin/env python

from plico.client.hackerable_client import HackerableClient
from plico_dm.client.abstract_deformable_mirror_client import \
    AbstractDeformableMirrorClient
from plico.rpc.abstract_remote_procedure_call import \
    AbstractRemoteProcedureCall
from plico.utils.logger import Logger
from plico.utils.decorator import override, returns
from plico_dm.utils.timeout import Timeout
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus
from plico.client.serverinfo_client import ServerInfoClient




class DeformableMirrorClient(AbstractDeformableMirrorClient,
                             HackerableClient, ServerInfoClient):

    def __init__(self,
                 rpcHandler,
                 sockets):
        assert isinstance(rpcHandler, AbstractRemoteProcedureCall)

        self._rpcHandler= rpcHandler
        self._requestSocket= sockets.serverRequest()
        self._statusSocket= sockets.serverStatus()
        self._logger= Logger.of('DeformableMirrorClient')

        HackerableClient.__init__(self,
                                  self._rpcHandler,
                                  self._requestSocket,
                                  self._logger)
        ServerInfoClient.__init__(self,
                                  self._rpcHandler,
                                  self._requestSocket,
                                  self._logger)


    @override
    def enableControlLoop(self,
                          boolEnableOrDisable,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'enableControlLoop', [boolEnableOrDisable],
            timeout=timeoutInSec)



    @override
    def loadShapeSequence(self,
                          shapeSequence,
                          timeStepInSeconds,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'loadShapeSequence', [shapeSequence, timeStepInSeconds],
            timeout=timeoutInSec)


    @override
    def startShapeSequence(self,
                           timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'startShapeSequence', [],
            timeout=timeoutInSec)


    @override
    def stopShapeSequence(self,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'stopShapeSequence', [],
            timeout=timeoutInSec)


    @override
    def setShape(self,
                 command,
                 timeoutInSec=Timeout.MIRROR_SET_SHAPE):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'setShape', [command],
            timeout=timeoutInSec)


    @override
    def getShape(self, timeoutInSec=Timeout.MIRROR_GET_SHAPE):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getShape', [],
            timeout=timeoutInSec)


    @override
    def getNumberOfModes(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return int(self.getStatus(timeoutInSec).numberOfModes())


    @override
    @returns(DeformableMirrorStatus)
    def getStatus(self, timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.receivePickable(
            self._statusSocket,
            timeoutInSec)


    @override
    def getSnapshot(self,
                    prefix,
                    timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getSnapshot', [prefix],
            timeout=timeoutInSec)
