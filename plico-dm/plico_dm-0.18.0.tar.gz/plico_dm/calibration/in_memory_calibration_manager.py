from plico.utils.decorator import override, returnsNone, returns
from plico_dm.types.modal_basis import ModalBasis
from plico_dm.calibration.abstract_calibration_manager import \
    AbstractCalibrationManager
import numpy



class InMemoryCalibrationManager(AbstractCalibrationManager):

    def __init__(self):
        self._modalBasisDict= {}
        self._zonalCommandDict= {}


    @override
    @returnsNone
    def saveModalBasis(self, tag, modalBasis):
        self._modalBasisDict[tag]= modalBasis


    @override
    @returns(ModalBasis)
    def loadModalBasis(self, tag):
        return self._modalBasisDict[str(tag)]


    @override
    @returnsNone
    def saveZonalCommand(self, tag, zonalCommand):
        self._zonalCommandDict[tag]= zonalCommand


    @override
    @returns(numpy.ndarray)
    def loadZonalCommand(self, tag):
        return self._zonalCommandDict[str(tag)]
