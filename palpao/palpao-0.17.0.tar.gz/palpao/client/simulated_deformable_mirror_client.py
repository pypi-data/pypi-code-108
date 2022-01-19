import numpy as np
from plico.utils.decorator import override, returns
from palpao.client.abstract_deformable_mirror_client import \
    AbstractDeformableMirrorClient
from palpao.utils.timeout import Timeout
import time
from palpao.types.deformable_mirror_status import DeformableMirrorStatus



class SimulatedDeformableMirrorClient(AbstractDeformableMirrorClient):

    N_MODES= 4

    def __init__(self, timeModule=time):
        self._timeMod= timeModule
        self._shape= np.zeros(self.N_MODES)
        self._commandCounter= 0
        self._isControlLoopEnabled= False
        self._isShapeSequenceEnabled= False
        self._shapeSeq= np.zeros(self.N_MODES).reshape((
            self.N_MODES, 1))
        self._nElementsShapeSeq= 1
        self._seqTimeStepInSeconds= 1
        self._shapeSeqIdx= 0
        self._timeStampSequence= 0


    @override
    def enableControlLoop(self,
                          boolEnableOrDisable,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isControlLoopEnabled= boolEnableOrDisable


    @override
    def loadShapeSequence(self,
                          shapeSequence,
                          timeStepInSeconds,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        self._shapeSeq= shapeSequence
        self._seqTimeStepInSeconds= timeStepInSeconds
        self._shapeSeqIdx= 0
        self._nElementsShapeSeq= self._shapeSeq.shape[1]


    @override
    def startShapeSequence(self,
                           timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isShapeSequenceEnabled= True
        self._timeStampSequence= self._timeMod.time()


    @override
    def stopShapeSequence(self,
                          timeoutInSec=Timeout.GENERIC_COMMAND):
        self._isShapeSequenceEnabled= False


    @override
    def setShape(self,
                 command,
                 timeoutInSec=Timeout.MIRROR_SET_SHAPE):
        self._shape= command.copy()
        self._commandCounter+= 1


    @override
    def getShape(self, timeoutInSec=Timeout.MIRROR_GET_SHAPE):
        shape= self._shape.copy()
        if self._isShapeSequenceEnabled:
            now= self._timeMod.time()
            nSteps= int((now - self._timeStampSequence) /
                        self._seqTimeStepInSeconds)
            seqIdx= nSteps % self._nElementsShapeSeq
            shape += self._shapeSeq[:, seqIdx]
        return shape


    @override
    def getNumberOfModes(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self.N_MODES


    @override
    @returns(DeformableMirrorStatus)
    def getStatus(self, timeoutInSec=Timeout.MIRROR_GET_STATUS):
        return DeformableMirrorStatus(self._shape,
                                      self._commandCounter)



    @override
    def getSnapshot(self):
        return {}
