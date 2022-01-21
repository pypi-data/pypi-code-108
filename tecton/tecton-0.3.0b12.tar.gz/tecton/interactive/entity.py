from typing import List
from typing import Optional

from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton_proto.data import entity_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import GetEntityRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetEntitySummaryRequest
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger

logger = get_logger("Entity")


class Entity(Fco):
    """
    Entity class.

    An Entity is a class that represents an Entity that is being modelled in Tecton.
    Entities are used to index and organize features - a :class:`FeatureView`
    contains at least one Entity.

    Entities contain metadata about *join keys*, which represent the columns
    that are used to join features together.
    """

    _entity_proto: entity_pb2.Entity = None

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_entity` """

    @classmethod
    def _from_proto(cls, entity_proto: entity_pb2.Entity) -> "Entity":
        """
        Instantiates a new Entity object.

        `Entity` instance always corresponds to the existing registered Entity in the Database.
        """
        obj = cls.__new__(cls)
        obj._entity_proto = entity_proto
        return obj

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "entity"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "entities"

    @property
    def _fco_metadata(self):
        return self._entity_proto.fco_metadata

    def __repr__(self):
        return f"Entity(name='{self.name}', join_keys={self.join_keys}, description='{self.description}')"

    @property  # type: ignore
    @sdk_public_method
    def join_keys(self) -> List[str]:
        """
        Returns the join keys of this entity.
        """
        return self._entity_proto.join_keys

    @sdk_public_method
    def summary(self) -> Displayable:
        """
        Displays a human readable summary of this Entity.
        """
        request = GetEntitySummaryRequest()
        request.fco_locator.id.CopyFrom(self._entity_proto.entity_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetEntitySummary(request)
        return Displayable.from_fco_summary(response.fco_summary)

    @property
    def id(self) -> str:
        """
        Returns ID of the database entity entry.
        """
        return IdHelper.to_string(self._entity_proto.entity_id)


@sdk_public_method
def get_entity(name: str, workspace_name: Optional[str] = None) -> Entity:
    """
    Fetch an existing :class:`Entity` by name.

    :param name: Unique name for an existing entity.

    :raises TectonValidationError: if an entity with given name does not exist.
    """
    request = GetEntityRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetEntity(request)

    if not response.HasField("entity"):
        raise errors.FCO_NOT_FOUND(Entity, name)

    return Entity._from_proto(response.entity)
