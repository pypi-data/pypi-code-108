from typing import List

from tecton_proto.data.feature_view_pb2 import OnlineServingIndex as OnlineServingIndexProto


class OnlineServingIndex:
    """
    Defines join keys that can be used with ``query_features``.
    This class contains set of partial join keys that will be indexed
    and queryable in FeatureServices that include this feature definition.
    For example, for a feature definition that has join keys ["user", "page"],
    if we pass OnlineServingIndex(["user"]), we will be able to invoke
    feature_service.query_features({"user": "user_1"})
    and get back feature vectors for all user-page pairs where user="user_1".
    """

    def __init__(self, join_keys: List[str]):
        """
        Create a new OnlineServingIndex.

        :param join_keys: The partial join keys that will be indexed in the online feature store
        """
        self.join_keys = join_keys

    @classmethod
    def from_proto(cls, proto: OnlineServingIndexProto):
        """Instantiates object from the provided proto object."""
        return cls(list(proto.join_keys))

    def to_proto(self):
        """Returns proto object created from the existing object."""
        proto = OnlineServingIndexProto()
        proto.join_keys.extend(self.join_keys)
        return proto

    def __str__(self):
        return str(self.join_keys)

    def __repr__(self):
        return str(self)
