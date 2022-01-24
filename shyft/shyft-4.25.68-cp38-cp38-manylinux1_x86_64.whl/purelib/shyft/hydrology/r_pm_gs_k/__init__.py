from ._r_pm_gs_k import *
from ...time_series import ByteVector
# Fix up types that we need attached to the model
RPMGSKStateVector.push_back = lambda self, x: self.append(x)
RPMGSKStateVector.size = lambda self: len(self)


RPMGSKModel.cell_t = RPMGSKCellAll
RPMGSKParameter.map_t = RPMGSKParameterMap
RPMGSKModel.parameter_t = RPMGSKParameter
RPMGSKModel.state_t = RPMGSKState
RPMGSKModel.state_with_id_t = RPMGSKStateWithId
RPMGSKModel.state = property(lambda self:RPMGSKCellAllStateHandler(self.get_cells()))
RPMGSKModel.statistics = property(lambda self: RPMGSKCellAllStatistics(self.get_cells()))

RPMGSKModel.gamma_snow_state = property(lambda self: RPMGSKCellGammaSnowStateStatistics(self.get_cells()))
RPMGSKModel.gamma_snow_response = property(lambda self: RPMGSKCellGammaSnowResponseStatistics(self.get_cells()))
RPMGSKModel.penman_monteith_response = property(lambda self: RPMGSKCellPenmanMonteithResponseStatistics(self.get_cells()))
RPMGSKModel.actual_evaptranspiration_response=property(lambda self: RPMGSKCellActualEvapotranspirationResponseStatistics(self.get_cells()))
RPMGSKModel.kirchner_state = property(lambda self: RPMGSKCellKirchnerStateStatistics(self.get_cells()))

RPMGSKOptModel.cell_t = RPMGSKCellOpt
RPMGSKOptModel.parameter_t = RPMGSKParameter
RPMGSKOptModel.state_t = RPMGSKState
RPMGSKOptModel.state_with_id_t = RPMGSKStateWithId
RPMGSKOptModel.state = property(lambda self:RPMGSKCellOptStateHandler(self.get_cells()))
RPMGSKOptModel.statistics = property(lambda self:RPMGSKCellOptStatistics(self.get_cells()))

RPMGSKOptModel.optimizer_t = RPMGSKOptimizer
RPMGSKOptModel.full_model_t =RPMGSKModel
RPMGSKModel.opt_model_t =RPMGSKOptModel
RPMGSKModel.create_opt_model_clone = lambda self: create_opt_model_clone(self)
#RPMGSKModel.create_opt_model_clone.__doc__ = create_opt_model_clone.__doc__
RPMGSKOptModel.create_full_model_clone = lambda self: create_full_model_clone(self)
#RPMGSKOptModel.create_full_model_clone.__doc__ = create_full_model_clone.__doc__


RPMGSKCellAll.vector_t = RPMGSKCellAllVector
RPMGSKCellOpt.vector_t = RPMGSKCellOptVector
RPMGSKState.vector_t = RPMGSKStateVector

#decorate StateWithId for serialization support
def serialize_to_bytes(state_with_id_vector:RPMGSKStateWithIdVector)->ByteVector:
    if not isinstance(state_with_id_vector,RPMGSKStateWithIdVector):
        raise RuntimeError("supplied argument must be of type RPMGSKStateWithIdVector")
    return serialize(state_with_id_vector)

def __serialize_to_str(state_with_id_vector:RPMGSKStateWithIdVector)->str:
    return str(serialize_to_bytes(state_with_id_vector))  # returns hex-string formatted vector

def __deserialize_from_str(s:str)->RPMGSKStateWithIdVector:
    return deserialize_from_bytes(ByteVector.from_str(s))

RPMGSKStateWithIdVector.serialize_to_bytes = lambda self: serialize_to_bytes(self)
RPMGSKStateWithIdVector.serialize_to_str = lambda self: __serialize_to_str(self)
RPMGSKStateWithIdVector.state_vector = property(lambda self: extract_state_vector(self),doc="extract_state_vector.__doc__")
RPMGSKStateWithIdVector.deserialize_from_str = __deserialize_from_str
RPMGSKStateWithId.vector_t = RPMGSKStateWithIdVector
def deserialize_from_bytes(bytes: ByteVector)->RPMGSKStateWithIdVector:
    if not isinstance(bytes,ByteVector):
        raise RuntimeError("Supplied type must be a ByteVector, as created from serialize_to_bytes")
    states=RPMGSKStateWithIdVector()
    deserialize(bytes,states)
    return states

__all__=[
    'RPMGSKStateVector',
    'RPMGSKStateWithId',
    'RPMGSKStateWithIdVector',
    'RPMGSKCellAll',
    'RPMGSKCellOpt',
    'RPMGSKState',
    'RPMGSKModel',
    'RPMGSKOptModel',
    'RPMGSKParameter'
]