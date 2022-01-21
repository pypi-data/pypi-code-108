
from ..data.ls_dyna import DEForc, Elout, EloutObject, Glstat, Matsum, Nodout, RCForc, SBTout, SlipringOut, Secforc, Disbout, \
                           PartDisbout, Abstat, AbstatCPM, JointForc, Sleout, RigidBody, BoundaryCondition, JointType
from ..utils.constants import ObjectConstantsForData


class DataContainer:
    """class DataContainer
    store objects types

    Args:

    Returns:

    """
    _elout = None
    _elout_object = None
    _secforc = None
    _rcforc = None
    _deforc = None
    _nodout = None
    _joint_forc = None
    _joint_type = None
    _volume = None
    _sbtout = None
    _slipringout = None
    _matsum = None
    _glstat = None
    _disbout = None
    _part_disbout = None
    _abstat = None
    _abstat_cpm = None
    _sleout = None
    _rigid_body = None
    _boundary_condition = None

    @staticmethod
    def get_data(name):
        """

        Args:
          name: 

        Returns:
          Object on the given name

        """
        if name == ObjectConstantsForData.ELEMENT:
            return DataContainer._elout
        elif name == ObjectConstantsForData.ELEMENTOBJECT:
            return DataContainer._elout_object
        elif name == ObjectConstantsForData.CROSS_SECTION:
            return DataContainer._secforc
        elif name == ObjectConstantsForData.DISCRETE:
            return DataContainer._deforc
        elif name == ObjectConstantsForData.NODE:
            return DataContainer._nodout
        elif name == ObjectConstantsForData.JOINT:
            return DataContainer._joint_forc
        elif name == ObjectConstantsForData.JOINT_TYPE:
            return DataContainer._joint_type
        elif name == ObjectConstantsForData.SEAT_BELT:
            return DataContainer._sbtout
        elif name == ObjectConstantsForData.SLIP_RING:
            return DataContainer._slipringout
        elif name == ObjectConstantsForData.CONTACT:
            return DataContainer._rcforc
        elif name == ObjectConstantsForData.ENERGY_PART:
            return DataContainer._matsum
        elif name == ObjectConstantsForData.ENERGY_GLOBAL:
            return DataContainer._glstat
        elif name == ObjectConstantsForData.DISBOUT:
            return DataContainer._disbout
        elif name == ObjectConstantsForData.DISBOUT_PART:
            return DataContainer._part_disbout
        elif name == ObjectConstantsForData.AIRBAG:
            return DataContainer._abstat
        elif name == ObjectConstantsForData.AIRBAG_CPM:
            return DataContainer._abstat_cpm
        elif name == ObjectConstantsForData.SLEOUT:
            return DataContainer._sleout
        elif name == ObjectConstantsForData.RIGID_BODY:
            return DataContainer._rigid_body
        elif name == ObjectConstantsForData.BOUNDARY_CONDITION:
            return DataContainer._boundary_condition
        else:
            return None

    @staticmethod
    def init_all_data_sources(binout, logger, dynasaur_def, volume_path):
        """init all data sources

        Args:
          binout: 
          logger: 
          dynasaur_def: 
          volume_path: 

        Returns:

        """
        DataContainer._secforc = Secforc(binout, logger, dynasaur_def)
        DataContainer._elout = Elout(binout, logger, dynasaur_def)
        DataContainer._elout_object = EloutObject(binout, logger, dynasaur_def, volume_path=volume_path)
        DataContainer._nodout = Nodout(binout, logger, dynasaur_def)
        DataContainer._joint_forc = JointForc(binout, logger, dynasaur_def)
        DataContainer._joint_type = JointType(binout, logger, dynasaur_def)
        DataContainer._deforc = DEForc(binout, logger, dynasaur_def)
        DataContainer._disbout = Disbout(binout, logger, dynasaur_def)
        DataContainer._part_disbout = PartDisbout(binout, logger, dynasaur_def)
        DataContainer._rcforc = RCForc(binout, logger, dynasaur_def)
        DataContainer._sbtout = SBTout(binout, logger, dynasaur_def)
        DataContainer._slipringout = SlipringOut(binout, logger, dynasaur_def)
        DataContainer._matsum = Matsum(binout, logger, dynasaur_def)
        DataContainer._glstat = Glstat(binout, logger, dynasaur_def)
        DataContainer._abstat = Abstat(binout, logger, dynasaur_def)
        DataContainer._abstat_cpm = AbstatCPM(binout, logger, dynasaur_def)
        DataContainer._sleout = Sleout(binout, logger, dynasaur_def)
        DataContainer._rigid_body = RigidBody(binout, logger, dynasaur_def)
        DataContainer._boundary_condition = BoundaryCondition(binout, logger, dynasaur_def)

