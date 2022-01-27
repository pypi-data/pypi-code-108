from ._pt_st_k import *
from ...time_series import ByteVector
# Fix up types that we need attached to the model
PTSTKStateVector.push_back = lambda self, x: self.append(x)
PTSTKStateVector.size = lambda self: len(self)

PTSTKModel.cell_t = PTSTKCellAll
PTSTKParameter.map_t = PTSTKParameterMap
PTSTKModel.parameter_t = PTSTKParameter
PTSTKModel.state_t = PTSTKState
PTSTKModel.state_with_id_t = PTSTKStateWithId
PTSTKModel.state = property(lambda self:PTSTKCellAllStateHandler(self.get_cells()))
PTSTKModel.statistics = property(lambda self: PTSTKCellAllStatistics(self.get_cells()))

PTSTKModel.snow_tiles_state = property(lambda self: PTSTKCellSnowTilesStateStatistics(self.get_cells()))
PTSTKModel.snow_tiles_response = property(lambda self: PTSTKCellSnowTilesResponseStatistics(self.get_cells()))
PTSTKModel.priestley_taylor_response = property(lambda self: PTSTKCellPriestleyTaylorResponseStatistics(self.get_cells()))
PTSTKModel.actual_evaptranspiration_response=property(lambda self: PTSTKCellActualEvapotranspirationResponseStatistics(self.get_cells()))
PTSTKModel.kirchner_state = property(lambda self: PTSTKCellKirchnerStateStatistics(self.get_cells()))

PTSTKOptModel.cell_t = PTSTKCellOpt
PTSTKOptModel.parameter_t = PTSTKParameter
PTSTKOptModel.state_t = PTSTKState
PTSTKOptModel.state_with_id_t = PTSTKStateWithId
PTSTKOptModel.state = property(lambda self:PTSTKCellOptStateHandler(self.get_cells()))
PTSTKOptModel.statistics = property(lambda self:PTSTKCellOptStatistics(self.get_cells()))

PTSTKOptModel.optimizer_t = PTSTKOptimizer

PTSTKOptModel.full_model_t =PTSTKModel
PTSTKModel.opt_model_t =PTSTKOptModel
PTSTKModel.create_opt_model_clone = lambda self: create_opt_model_clone(self)
#PTSTKModel.create_opt_model_clone.__doc__ = create_opt_model_clone.__doc__
PTSTKOptModel.create_full_model_clone = lambda self: create_full_model_clone(self)
#PTSTKOptModel.create_full_model_clone.__doc__ = create_full_model_clone.__doc__

PTSTKCellAll.vector_t = PTSTKCellAllVector
PTSTKCellOpt.vector_t = PTSTKCellOptVector
PTSTKState.vector_t = PTSTKStateVector
#PTSTKState.serializer_t= PTSTKStateIo

#decorate StateWithId for serialization support
def serialize_to_bytes(state_with_id_vector:PTSTKStateWithIdVector)->ByteVector:
    if not isinstance(state_with_id_vector,PTSTKStateWithIdVector):
        raise RuntimeError("supplied argument must be of type PTSTKStateWithIdVector")
    return serialize(state_with_id_vector)

def __serialize_to_str(state_with_id_vector:PTSTKStateWithIdVector)->str:
    return str(serialize_to_bytes(state_with_id_vector))  # returns hex-string formatted vector

def __deserialize_from_str(s:str)->PTSTKStateWithIdVector:
    return deserialize_from_bytes(ByteVector.from_str(s))

PTSTKStateWithIdVector.serialize_to_bytes = lambda self: serialize_to_bytes(self)
PTSTKStateWithIdVector.serialize_to_str = lambda self: __serialize_to_str(self)
PTSTKStateWithIdVector.deserialize_from_str = __deserialize_from_str
PTSTKStateWithIdVector.state_vector = property(lambda self: extract_state_vector(self),doc="extract_state_vector.__doc__")
PTSTKStateWithId.vector_t = PTSTKStateWithIdVector

def deserialize_from_bytes(bytes: ByteVector)->PTSTKStateWithIdVector:
    if not isinstance(bytes,ByteVector):
        raise RuntimeError("Supplied type must be a ByteVector, as created from serialize_to_bytes")
    states=PTSTKStateWithIdVector()
    deserialize(bytes,states)
    return states
__all__=[
    'PTSTKStateVector',
    'PTSTKStateWithId',
    'PTSTKStateWithIdVector',
    'PTSTKCellAll',
    'PTSTKCellOpt',
    'PTSTKState',
    'PTSTKModel',
    'PTSTKOptModel',
    'PTSTKParameter'
]