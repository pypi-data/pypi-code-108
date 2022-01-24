from ._r_pt_gs_k import *
from ...time_series import ByteVector
# Fix up types that we need attached to the model
RPTGSKStateVector.push_back = lambda self, x: self.append(x)
RPTGSKStateVector.size = lambda self: len(self)


RPTGSKModel.cell_t = RPTGSKCellAll
RPTGSKParameter.map_t = RPTGSKParameterMap
RPTGSKModel.parameter_t = RPTGSKParameter
RPTGSKModel.state_t = RPTGSKState
RPTGSKModel.state_with_id_t = RPTGSKStateWithId
RPTGSKModel.state = property(lambda self:RPTGSKCellAllStateHandler(self.get_cells()))
RPTGSKModel.statistics = property(lambda self: RPTGSKCellAllStatistics(self.get_cells()))

RPTGSKModel.gamma_snow_state = property(lambda self: RPTGSKCellGammaSnowStateStatistics(self.get_cells()))
RPTGSKModel.gamma_snow_response = property(lambda self: RPTGSKCellGammaSnowResponseStatistics(self.get_cells()))
RPTGSKModel.priestley_taylor_response = property(lambda self: RPTGSKCellPriestleyTaylorResponseStatistics(self.get_cells()))
RPTGSKModel.radiation_response = property(lambda self: RPTGSKCellRadiationResponseStatistics(self.get_cells()))
RPTGSKModel.actual_evaptranspiration_response=property(lambda self: RPTGSKCellActualEvapotranspirationResponseStatistics(self.get_cells()))
RPTGSKModel.kirchner_state = property(lambda self: RPTGSKCellKirchnerStateStatistics(self.get_cells()))

RPTGSKOptModel.cell_t = RPTGSKCellOpt
RPTGSKOptModel.parameter_t = RPTGSKParameter
RPTGSKOptModel.state_t = RPTGSKState
RPTGSKOptModel.state_with_id_t = RPTGSKStateWithId
RPTGSKOptModel.state = property(lambda self:RPTGSKCellOptStateHandler(self.get_cells()))
RPTGSKOptModel.statistics = property(lambda self:RPTGSKCellOptStatistics(self.get_cells()))

RPTGSKOptModel.optimizer_t = RPTGSKOptimizer
RPTGSKOptModel.full_model_t =RPTGSKModel
RPTGSKModel.opt_model_t =RPTGSKOptModel
RPTGSKModel.create_opt_model_clone = lambda self: create_opt_model_clone(self)
#RPTGSKModel.create_opt_model_clone.__doc__ = create_opt_model_clone.__doc__
RPTGSKOptModel.create_full_model_clone = lambda self: create_full_model_clone(self)
#RPTGSKOptModel.create_full_model_clone.__doc__ = create_full_model_clone.__doc__


RPTGSKCellAll.vector_t = RPTGSKCellAllVector
RPTGSKCellOpt.vector_t = RPTGSKCellOptVector
RPTGSKState.vector_t = RPTGSKStateVector

#decorate StateWithId for serialization support
def serialize_to_bytes(state_with_id_vector:RPTGSKStateWithIdVector)->ByteVector:
    if not isinstance(state_with_id_vector,RPTGSKStateWithIdVector):
        raise RuntimeError("supplied argument must be of type RPTGSKStateWithIdVector")
    return serialize(state_with_id_vector)

def __serialize_to_str(state_with_id_vector:RPTGSKStateWithIdVector)->str:
    return str(serialize_to_bytes(state_with_id_vector))  # returns hex-string formatted vector

def __deserialize_from_str(s:str)->RPTGSKStateWithIdVector:
    return deserialize_from_bytes(ByteVector.from_str(s))

RPTGSKStateWithIdVector.serialize_to_bytes = lambda self: serialize_to_bytes(self)
RPTGSKStateWithIdVector.serialize_to_str = lambda self: __serialize_to_str(self)
RPTGSKStateWithIdVector.state_vector = property(lambda self: extract_state_vector(self),doc="extract_state_vector.__doc__")
RPTGSKStateWithIdVector.deserialize_from_str = __deserialize_from_str
RPTGSKStateWithId.vector_t = RPTGSKStateWithIdVector
def deserialize_from_bytes(bytes: ByteVector)->RPTGSKStateWithIdVector:
    if not isinstance(bytes,ByteVector):
        raise RuntimeError("Supplied type must be a ByteVector, as created from serialize_to_bytes")
    states=RPTGSKStateWithIdVector()
    deserialize(bytes,states)
    return states
__all__=[
    'RPTGSKStateVector',
    'RPTGSKStateWithId',
    'RPTGSKStateWithIdVector',
    'RPTGSKCellAll',
    'RPTGSKCellOpt',
    'RPTGSKState',
    'RPTGSKModel',
    'RPTGSKOptModel',
    'RPTGSKParameter'
]