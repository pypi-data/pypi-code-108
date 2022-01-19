import abc
from plico.utils.decorator import returnsNone, returns, returnsForExample
from plico_dm.types.deformable_mirror_status import DeformableMirrorStatus
from six import with_metaclass




class SnapshotEntry(object):
    COMMAND_COUNTER= "COMMAND_COUNTER"
    SERIAL_NUMBER= "SERIAL_NUMBER"
    STEP_COUNTER= "STEP_COUNTER"



class AbstractDeformableMirrorClient(with_metaclass(abc.ABCMeta, object)):
    """
    Interface to control a deformable mirror


    Assume a modal control of the DM.

    """

    @abc.abstractmethod
    def getNumberOfModes(self):
        """ Number of modes of the deformable mirror

        Return the number of modes of the deformable mirror.
        number of degrees of freedom.

        Return:
            numberOfModes (int): the number of modes of the deformable mirror.
        """
        assert False


    @abc.abstractmethod
    @returnsNone
    def setShape(self, command):
        """ Set Deformable Mirror Shape

        Send to the controller the request to set the DM shape

        Parameters:
            command (:obj:ndarray): an array containing the required value for the actuators/modes
                The size of the array must be equal to the number of modes of the DM


        """
        assert False


    @abc.abstractmethod
    @returnsNone
    def getShape(self):
        """ Get Deformable Mirror Shape

        Send to the controller the request to set the DM shape

        Return:
            shape (:obj:ndarray): an array containing the measured value for the actuators/modes
                The size of the array must be equal to the number of modes of the DM

        The value are measured if the DM has an internal metrology on position
        The shape sequence is taken into account.

        """
        assert False


    @abc.abstractmethod
    def loadShapeSequence(self, shapeSequence, timeStepInSeconds):
        """ Load a shape sequence to be applied to the mirror

        Every element of the sequence correspond to a DM shape
        After timeStepInSeconds the next element of the sequence is applied
        The sequence is executed ciclycally until 

        The shape sequence is added to the current shape
        The shape sequence is applied as a circular buffer 

        Parameters:
            shapeSequence (:obj:ndarray): an array containing the shape sequence value for the actuators/modes
                The array size is (nModes, nTimeSteps)
            timeStepInSeconds (float): updating interval of sequence.
                Every timeStepInSeconds the controller applies the next column of shapeSequence
        """
        assert False


    @abc.abstractmethod
    @returnsNone
    def startShapeSequence(self):
        assert False


    @abc.abstractmethod
    @returnsNone
    def stopShapeSequence(self):
        assert False


    @abc.abstractmethod
    @returnsNone
    def enableControlLoop(self, boolEnableOrDisable):
        """ Enable control loop

        If the deformable mirror controller has position feedback, 
        enable the position control loop
        Else, raise TypeError
        """
        assert False


    @abc.abstractmethod
    @returnsForExample({'WFS_CAMERA.EXPOSURE_TIME_MS': 10})
    def getSnapshot(self, prefix):
        assert False


    @abc.abstractmethod
    @returns(DeformableMirrorStatus)
    def getStatus(self):
        assert False
