from typing import List

from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.fco_pb2 import Fco
from tecton_proto.data.fco_pb2 import FcoContainer as FcoContainerProto
from tecton_proto.data.feature_view_pb2 import FeatureView as FeatureViewProto
from tecton_proto.data.new_transformation_pb2 import NewTransformation as Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as DataSourceProto
from tecton_spark.id_helper import IdHelper


class FcoWrapper:
    """
    A wrapper class for data.Fco proto, contains convenience accessors
    """

    _fco: Fco

    def __init__(self, fco: Fco):
        self._fco = fco

    @property
    def id(self) -> Id:
        if self._fco.HasField("virtual_data_source"):
            return self._fco.virtual_data_source.virtual_data_source_id
        elif self._fco.HasField("entity"):
            return self._fco.entity.entity_id
        elif self._fco.HasField("new_transformation"):
            return self._fco.new_transformation.transformation_id
        elif self._fco.HasField("feature_view"):
            return self._fco.feature_view.feature_view_id
        elif self._fco.HasField("feature_service"):
            return self._fco.feature_service.feature_service_id
        else:
            raise Exception("unexpected fco type")

    @property
    def inner(self):
        if self._fco.HasField("virtual_data_source"):
            return self._fco.virtual_data_source
        elif self._fco.HasField("entity"):
            return self._fco.entity
        elif self._fco.HasField("new_transformation"):
            return self._fco.new_transformation
        elif self._fco.HasField("feature_view"):
            return self._fco.feature_view
        elif self._fco.HasField("feature_service"):
            return self._fco.feature_service
        else:
            raise Exception("unexpected fco type")


class FcoContainer:
    """
    A wrapper class for FcoContainer proto, contains convenience accessors
    """

    _proto: FcoContainerProto
    _id_to_fco: {}

    def __init__(self, proto: FcoContainerProto):
        assert type(proto) == FcoContainerProto, type(proto)
        self._proto = proto
        self._id_to_fco = {}
        for fco_proto in self._proto.fcos:
            fco_wrapped = FcoWrapper(fco_proto)
            self._id_to_fco[IdHelper.to_string(fco_wrapped.id)] = fco_wrapped

    def get_by_id(self, id: str):
        """
        :return: inner (specific) FCO proto, e.g., Entity, or FeatureView
        """

        return self._id_to_fco[id].inner

    def get_by_ids(self, ids: List[str]):
        """
        :return: inner (specific) FCO protos, e.g., Entities, or FeatureViews
        """

        return [self.get_by_id(id) for id in ids]

    def get_single_root(self):
        """
        :return: inner (specific) FCO proto, pointed by the root_ids or None. Errors if len(root_ids) > 1
        """

        num_root_ids = len(self._proto.root_ids)
        if num_root_ids == 0:
            return None
        elif num_root_ids > 1:
            raise ValueError(f"Expected a single result but got $num_root_ids")
        else:
            id = IdHelper.to_string(self._proto.root_ids[0])
            return self.get_by_id(id)

    def get_root_fcos(self):
        """
        :return: inner (specific) FCO protos, pointed by the root_ids.
        """

        return [self.get_by_id(IdHelper.to_string(id)) for id in self._proto.root_ids]

    def get_all(self):
        """
        :return: all inner (specific) FCO protos
        """

        return [fco.inner for fco in self._id_to_fco.values()]


FCO_CONTAINER_EMTPY = FcoContainer(FcoContainerProto())


def _wrap_data_fco(inner_proto) -> Fco:
    fco = Fco()
    if isinstance(inner_proto, DataSourceProto):
        fco.virtual_data_source.CopyFrom(inner_proto)
    elif isinstance(inner_proto, Transformation):
        fco.new_transformation.CopyFrom(inner_proto)
    elif isinstance(inner_proto, FeatureViewProto):
        fco.feature_view.CopyFrom(inner_proto)
    else:
        raise Exception("Unsupported type " + str(type(inner_proto)))
    return fco


def create_fco_container(fco_protos: List) -> FcoContainerProto:
    proto = FcoContainerProto()
    for inner_fco_proto in fco_protos:
        wrapped_fco_proto = _wrap_data_fco(inner_fco_proto)
        proto.fcos.append(wrapped_fco_proto)
    return FcoContainer(proto)
