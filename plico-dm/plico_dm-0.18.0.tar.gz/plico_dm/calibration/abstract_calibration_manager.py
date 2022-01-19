import abc
from plico.utils.decorator import returns, returnsNone
from plico_dm.types.modal_basis import ModalBasis
from six import with_metaclass
import numpy



class AbstractCalibrationManager(with_metaclass(abc.ABCMeta, object)):

    @abc.abstractmethod
    @returns(ModalBasis)
    def loadModalBasis(self, tag):
        assert False


    @abc.abstractmethod
    @returnsNone
    def saveModalBasis(self, tag, modalBasis):
        assert False



    @abc.abstractmethod
    @returns(numpy.ndarray)
    def loadZonalCommand(self, tag):
        assert False


    @abc.abstractmethod
    @returnsNone
    def saveZonalCommand(self, tag, zonalCommand):
        assert False
