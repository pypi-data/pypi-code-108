import typing as T
from dgraph_orm import Node as DBNode
from pydantic import BaseModel, PrivateAttr

StrawberryType = T.TypeVar("StrawberryType")
NodeType = T.TypeVar("NodeType", bound=DBNode)
PydanticType = T.TypeVar("PydanticType", bound=BaseModel)


class LairException(Exception):
    pass


def pydantic_to_straw(
    gql_cls: T.Type[StrawberryType], pyd_model: PydanticType
) -> StrawberryType:
    if pyd_model is None:
        raise LairException("pyd_model cannot be None")
    # this gets all fields that are not resolvers
    straw_type_defs_d = {
        field.name: field
        for field in gql_cls._type_definition.fields
        if field.base_resolver is None
    }
    fields_to_use = set(straw_type_defs_d.keys()) & set(pyd_model.__fields__.keys())
    d = {}
    for field_name in fields_to_use:
        val = getattr(pyd_model, field_name)
        if isinstance(val, BaseModel):
            straw_type = straw_type_defs_d[field_name].type
            if of_type := getattr(straw_type, "of_type", None):
                straw_type = of_type
            val = pydantic_to_straw(gql_cls=straw_type, pyd_model=val)
        d[field_name] = val
    straw = gql_cls(**d)
    straw._node = pyd_model
    return straw


class Display(T.Generic[NodeType]):
    _node: NodeType = PrivateAttr(None)

    @classmethod
    def from_node(cls: T.Type[StrawberryType], node: NodeType) -> StrawberryType:
        return pydantic_to_straw(gql_cls=cls, pyd_model=node)

    @classmethod
    def from_node_or_none(
        cls: T.Type[StrawberryType], node: T.Optional[NodeType]
    ) -> T.Optional[StrawberryType]:
        if node is None:
            return None
        return cls.from_node(node=node)

    @classmethod
    def from_nodes(
        cls: T.Type[StrawberryType], nodes: T.List[NodeType]
    ) -> T.List[StrawberryType]:
        return [cls.from_node(node) for node in nodes]

    @property
    def node(self) -> NodeType:
        return self._node


DBType = T.TypeVar("DBType", bound=DBNode)
LayerNodeType = T.TypeVar("LayerNodeType", bound=DBNode)

# TODO prob rename this...
class Node(T.Generic[DBType]):
    @classmethod
    def from_db(cls: T.Type[LayerNodeType], model_db: DBType) -> LayerNodeType:
        # TODO make sure this covers everything
        # but must also transfer private fields and cache!
        n = cls(**model_db.dict())
        # for all private fields too
        # ooohhh, this is for the cache!
        for private_field in model_db.__private_attributes__.keys():
            setattr(n, private_field, getattr(model_db, private_field))
        return n

    @classmethod
    def from_db_or_none(
        cls: T.Type[LayerNodeType], model_db: T.Optional[DBType]
    ) -> T.Optional[LayerNodeType]:
        if not model_db:
            return None
        return cls.from_db(model_db)

    @classmethod
    def from_dbs(
        cls: T.Type[LayerNodeType], model_dbs: T.List[DBType]
    ) -> T.List[LayerNodeType]:
        return [cls.from_db(model_db) for model_db in model_dbs]
