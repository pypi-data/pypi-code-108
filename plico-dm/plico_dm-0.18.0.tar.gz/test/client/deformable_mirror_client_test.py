#!/usr/bin/env python
import unittest
import numpy as np
from plico.utils.decorator import override
from plico.rpc.dummy_remote_procedure_call import DummyRpcHandler
from plico.rpc.dummy_sockets import DummySockets
from plico_dm.client.deformable_mirror_client import DeformableMirrorClient
from plico_dm.utils.timeout import Timeout
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus



class TesterRpcHandler(DummyRpcHandler):

    def __init__(self):
        self._sendRequestHistory= []
        self._receivePickableHistory= []
        self._sendRequestCounter= 0
        self._receivePickableCounter= 0


    @override
    def sendRequest(self, socket, command, args, timeout=1):
        self._sendRequestHistory.append(
            (socket, command, args, timeout))
        self._sendRequestCounter += 1


    @override
    def receivePickable(self, socket, timeout=1):
        self._receivePickableCounter+= 1
        self._receivePickableHistory.append(
            (socket, timeout))
        return self._objToReturnWithReceivePickable


    def getLastSendRequestArguments(self):
        return self._sendRequestHistory[-1]


    def getLastReceivePickableArguments(self):
        return self._receivePickableHistory[-1]


    def wantsPickable(self, objToReturnWithReceivePickable):
        self._objToReturnWithReceivePickable= \
            objToReturnWithReceivePickable


class MyRpcHandler(TesterRpcHandler):
    pass


class MySockets(DummySockets):
    pass


class DeformableMirrorClientTest(unittest.TestCase):


    def setUp(self):
        self._rpc= MyRpcHandler()
        self._sockets= MySockets()
        self._client= DeformableMirrorClient(self._rpc, self._sockets)


    def tearDown(self):
        pass


    def testSetShape(self):
        mirrorWantedShape= np.identity(4)
        self._client.setShape(mirrorWantedShape)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'setShape',
             [mirrorWantedShape],
             Timeout.MIRROR_SET_SHAPE))


    def testGetPosition(self):
        timeoutInSec= 12
        _= self._client.getShape(timeoutInSec)
        self.assertEqual(
            self._rpc.getLastSendRequestArguments(),
            (self._sockets.serverRequest(),
             'getShape',
             [],
             timeoutInSec))


    def testGetStatus(self):
        wantedInstrumentStatus= DeformableMirrorStatus(
            12, 34, 'foo', 'tux')
        self._rpc.wantsPickable(wantedInstrumentStatus)

        timeoutInSec= 22
        gotInstrumentStatus= self._client.getStatus(timeoutInSec)
        self.assertEqual(
            wantedInstrumentStatus, gotInstrumentStatus)

        self.assertEqual(
            self._rpc.getLastReceivePickableArguments(),
            (self._sockets.serverStatus(),
             timeoutInSec))


if __name__ == "__main__":
    unittest.main()
