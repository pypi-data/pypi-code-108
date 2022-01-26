from __future__ import annotations
import typing as T
import json
import time
from pydantic import BaseModel, PrivateAttr
from fastapi.encoders import jsonable_encoder
from dgraph_orm import GQLException
from devtools import debug
from dgraph_orm.ACL.client import DgraphClient


def d_rez(refresh: bool = False, use_stale: bool = False, returns: T.Type = None):
    """The problem w this is it does not do types"""

    def outer(f: T.Callable):
        def inner(
            *args, refresh: bool = refresh, use_stale: bool = use_stale, **kwargs
        ) -> returns:
            resolver = f(*args, **kwargs)
            return args[0].resolve(
                name=f.__name__, resolver=resolver, refresh=refresh, use_stale=use_stale
            )

        return inner

    return outer


class Cache(BaseModel):
    # val: T.Union[Node, T.List[Node], None]
    val: T.Any
    resolver: Resolver
    timestamp: float
    raw_gql: str


class CacheManager(BaseModel):
    cache: T.Dict[str, Cache] = {}

    def remove(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]

    def add(self, *, key: str, resolver: Resolver, val: T.Any, gql_d: dict) -> None:
        self.cache[key] = Cache(
            val=val,
            resolver=resolver,
            timestamp=time.time(),
            raw_gql=json.dumps(jsonable_encoder(gql_d)),
        )

    def replace(self, key: str, cache: Cache) -> None:
        self.cache[key] = cache

    def get(self, key: str) -> T.Optional[Cache]:
        if key not in self.cache:
            return None
        return self.cache[key]

    def exists(self, key: str) -> bool:
        return key in self.cache

    def get_val(self, key: str) -> T.Optional[T.Union[Node, T.List[Node]]]:
        if c := self.cache[key]:
            return c.val

    def clear(self) -> None:
        self.cache = {}

    def is_empty(self) -> bool:
        return len(self.cache) == 0


from .gql_input import GQLInput


def parse_filter(filter: GQLInput) -> str:
    # print(f"{filter=}")
    return filter.to_gql_str()


def parse_nested_q(field_name: str, nested_q: BaseModel):
    if isinstance(nested_q, GQLInput):
        filter_s = parse_filter(nested_q)
        return f"{field_name}: {{ {filter_s} }}"
    outer_lst: T.List[str] = []
    for key, val in nested_q:
        if val is None:
            continue
        # for order, not filter
        if not isinstance(val, BaseModel):
            outer_lst.append(f"{key}: {val}")
            continue
        val: BaseModel
        inner_lst: T.List[str] = []
        for inner_key, inner_val in val.dict(exclude_none=True).items():
            inner_str = f"{inner_key}: {json.dumps(jsonable_encoder(inner_val))}"
            inner_lst.append(inner_str)
        outer_lst.append(f'{key}: {{ {",".join(inner_lst)} }}')
    return f'{field_name}: {{ {",".join(outer_lst)} }}'


class Params(BaseModel):
    def to_str(self) -> str:
        field_names = self.dict(exclude_none=True).keys()
        inner_params: T.List[str] = []
        for field_name in field_names:
            val = getattr(self, field_name)
            if isinstance(val, BaseModel):
                inner_params.append(parse_nested_q(field_name=field_name, nested_q=val))
            else:
                inner_params.append(
                    f"{field_name}: {json.dumps(jsonable_encoder(val))}"
                )
        if inner_params:
            return f'({",".join(inner_params)})'
        return ""

    class Config:
        validate_assignment = True


NodeModel = T.TypeVar("NodeModel", bound="Node")
ResolverType = T.TypeVar("ResolverType", bound="Resolver")
ResolverTempType = T.TypeVar("ResolverTempType", bound="Resolver")

OtherNodeType = T.TypeVar("OtherNodeType", bound="Node")

GQL_D = T.Dict[str, T.Any]
REL_D_INPUT = T.Dict[str, T.Optional[T.Union[OtherNodeType, T.List[OtherNodeType]]]]


class Node(BaseModel):
    _cache: CacheManager = PrivateAttr(default_factory=CacheManager)
    _used_resolver: ResolverType = PrivateAttr(None)
    _original_dict: dict = PrivateAttr(None)
    _deleted: bool = PrivateAttr(None)

    # id: str

    class Config:
        validate_assignment = True

    class GQL:
        # Rename this GQLConfig or something... just GQL probs
        typename: T.ClassVar[str]
        resolver: T.ClassVar[T.Type[ResolverType]]
        payload_node_name: str

        """ TODO fill the add and patch models in future for updating and adding"""
        add_model: T.Type[BaseModel]
        patch_model: T.Type[BaseModel]
        ref_model: T.Type[BaseModel]

        get_function_name: str = None
        query_function_name: str = None

        add_function_name: str = None
        update_function_name: str = None
        delete_function_name: str = None

        url: str
        uid_field_name: str

        dgraph_client: DgraphClient

    @property
    def _uid(self) -> T.Union[str, int]:
        return getattr(self, self.GQL.uid_field_name)

    @property
    def _uid_field_name(self) -> str:
        return self.GQL.uid_field_name

    @property
    def used_resolver(self) -> ResolverType:
        return self._used_resolver

    def __eq__(self, other: Node) -> bool:
        if not isinstance(other, Node):
            return False
        return f"{hash(self)}{self.json()}" == f"{hash(other)}{other.json()}"

    def __hash__(self) -> int:
        return hash(f"{self.__class__.__name__}{self._uid}")

    def to_ref(self, field_names: T.List[str] = None) -> GQL.ref_model:
        if field_names:
            return self.GQL.ref_model.parse_obj(
                {field_name: getattr(self, field_name) for field_name in field_names}
            )
        return self.GQL.ref_model.parse_obj(self.dict())

    @property
    def cache(self) -> CacheManager:
        return self._cache

    @staticmethod
    def nodes_by_typename() -> T.Dict[str, T.Type[Node]]:
        d = {}
        subs = Node.__subclasses__()
        for sub in subs:
            typename = sub.GQL.typename
            if typename in d:
                raise GQLException(
                    f"Two Nodes share the typename {typename}: ({sub.__name__}, {d[typename].__name__})"
                )
            d[typename] = sub
        return d

    def __repr__(self) -> str:
        r = super().__repr__()
        r = f"{r}, cache: {repr(self.cache)}" if not self.cache.is_empty() else r
        return r

    def get_root_resolver(self) -> T.Type[Resolver]:
        return Resolver.resolvers_by_typename()[self.GQL.typename]

    @staticmethod
    def should_use_new_resolver(
        old_r: Resolver, new_r: Resolver, strict: bool = False
    ) -> bool:
        old_r_j = old_r.json()
        new_r_j = new_r.json()
        if old_r_j == new_r_j:
            return False
        if strict:
            return True
        if old_r.json(exclude={"edges"}) != new_r.json(exclude={"edges"}):
            print(
                f'excluding children resolvers here..., {old_r.json(exclude={"edges"})=}, {new_r.json(exclude={"edges"})=}'
            )
            return True
        # now do the same for children
        for child_resolver_name in new_r.edges.__fields__.keys():
            new_child_resolver = getattr(new_r.edges, child_resolver_name)
            if new_child_resolver:
                old_child_resolver = getattr(old_r.edges, child_resolver_name)
                if not old_child_resolver:
                    return True
                if Node.should_use_new_resolver(
                    old_r=old_child_resolver,
                    new_r=new_child_resolver,
                    strict=strict,
                ):
                    return True
        return False

    async def resolve(
        self,
        name: str,
        resolver: T.Optional[ResolverTempType],
        refresh: bool = False,
        strict: bool = False,
        use_stale: bool = False,
    ) -> T.Optional[T.Union[NodeModel, T.Set[NodeModel]]]:
        root_resolver = self.GQL.resolver()
        if not resolver:
            resolver = root_resolver.edges.__fields__[name].type_()
        if refresh:
            self.cache.remove(name)
        # see if the resolvers do not match
        if cache := self.cache.get(name):
            if use_stale:
                return cache.val
            if self.should_use_new_resolver(
                old_r=cache.resolver, new_r=resolver, strict=strict
            ):
                print(
                    f"resolvers are different, removing {name} from cache, old: {cache.resolver=}, new: {resolver=}"
                )
                self.cache.remove(name)
        if not self.cache.exists(name):
            setattr(root_resolver.edges, name, resolver)
            obj = await root_resolver._get(kwargs_d={self._uid_field_name: self._uid})
            self.cache.replace(key=name, cache=obj.cache.get(name))
        return self.cache.get_val(name)

    @classmethod
    @property
    def resolver(cls) -> ResolverType:
        return cls.GQL.resolver()

    def hydrate(self, new_node: NodeModel) -> None:
        """Turns this node into the new node"""
        for field_name in new_node.__fields__.keys():
            new_field = getattr(new_node, field_name)
            old_field = getattr(self, field_name)
            if new_field != old_field:
                setattr(self, field_name, getattr(new_node, field_name))
        for private_attr_name in new_node.__private_attributes__.keys():
            setattr(self, private_attr_name, getattr(new_node, private_attr_name))

    """ADD REFRESH BEFORE ADDING ADD"""

    async def refresh(self: NodeModel) -> None:
        new_node = await self._used_resolver._get({self._uid_field_name: self._uid})
        self.hydrate(new_node=new_node)

    """CRUDS"""

    @staticmethod
    def make_set_and_remove_lists(
        original_list: T.Optional[set], new_list: T.Optional[set]
    ) -> T.Tuple[set, set]:
        # TODO should really ONLY be taking in SETS... fix later?
        # add all values from original list not in new list
        if original_list is None:
            original_list = set()
        if new_list is None:
            new_list = set()
        if type(original_list) is list:
            original_list = set(original_list)
        if type(new_list) is list:
            new_list = set(new_list)
        set_list = new_list - original_list
        remove_list = original_list - new_list
        return set_list, remove_list

    def base_set_remove_d(
        self, to_set: REL_D_INPUT = None, to_remove: REL_D_INPUT = None
    ) -> T.Tuple[GQL_D, GQL_D]:
        set_patch = self.GQL.patch_model()
        remove_patch = self.GQL.patch_model()

        current_d = self.dict()
        original_d = self._original_dict

        unset_key = "_UNSET_12398120"

        for field_name in self.GQL.patch_model.__fields__.keys():
            current_val = current_d.get(field_name, unset_key)
            original_val = original_d.get(field_name, unset_key)
            if current_val != original_val:
                # if list, if values have been removed, add to remove... if values have been added, keep
                if {type(current_val), type(original_val)} & {list, set, tuple}:
                    set_list, remove_list = self.make_set_and_remove_lists(
                        original_list=original_val, new_list=current_val
                    )
                    setattr(set_patch, field_name, set_list)
                    setattr(remove_patch, field_name, remove_list)
                else:
                    if current_val != unset_key:
                        # if current val is not unset -> always set
                        if current_val is not None:
                            setattr(set_patch, field_name, current_val)
                        else:
                            setattr(remove_patch, field_name, current_val)
                    else:
                        # current val is UNSET but original val is not
                        setattr(remove_patch, field_name, original_val)

        set_d: GQL_D = set_patch.dict(exclude_unset=True)
        remove_d: GQL_D = remove_patch.dict(exclude_unset=True)

        # stringify values before you include relationships which should not be stringified -> as long as they are REFS
        # i can see this being a problem if you're adding an embedded obj as a Ref ->
        # will deal w that when it comes later
        set_d = self.objs_to_str(set_d)
        remove_d = self.objs_to_str(remove_d)

        # now add relationship fields
        rel_set_d = self.make_gql_d_from_rel_d_input(rel_d_input=to_set or {})
        rel_remove_d = self.make_gql_d_from_rel_d_input(rel_d_input=to_remove or {})
        set_d.update(rel_set_d)
        remove_d.update(rel_remove_d)

        return set_d, remove_d

    async def update(self, given_resolver: ResolverType = None) -> bool:
        """
        Will usually be overwritten assuming there are relationships
        with this node (fill in to set and to remove with those relationship nodes)
        """
        if not self.GQL.update_function_name:
            raise GQLException(f"No update function given for {self.GQL.typename}")
        return await self._update(
            to_set={}, to_remove={}, given_resolver=given_resolver
        )

    @classmethod
    async def update_many(
        cls: T.Type[NodeModel],
        *,
        nodes: T.List[NodeModel],
        set_d: dict = None,
        remove_d: dict = None,
        given_resolver: ResolverType = None,
    ) -> bool:
        if not set_d and not remove_d:
            return False
        variables = {
            "set": jsonable_encoder(set_d) if set_d else {},
            "remove": jsonable_encoder(remove_d) if remove_d else {},
            "filter": {cls.GQL.uid_field_name: [node._uid for node in nodes]},
        }
        resolver = given_resolver or cls.GQL.resolver()
        query_str = resolver.make_update_mutation_str()
        debug(query_str)
        debug(variables)
        j = await cls.GQL.dgraph_client.execute(
            query_str=query_str, variables=variables
        )
        node_d_lst = j["data"][f"{cls.GQL.update_function_name}"][
            cls.GQL.payload_node_name
        ]
        if not node_d_lst:
            # raise Exception("No update was registered!!")
            print("NO UPDATE WAS REGISTERED")
            return False

        for og_node, node_d in zip(nodes, node_d_lst):
            new_node = resolver.parse_obj_nested(node_d)
            og_node.hydrate(new_node=new_node)

        return True

    @classmethod
    async def _add(
        cls: T.Type[NodeModel],
        *,
        inputs: T.List[GQL.add_model],
        given_resolver: T.Optional[ResolverType] = None,
        upsert: bool = None,
        use_one_time: bool = False,
    ) -> T.List[NodeModel]:
        resolver = given_resolver or cls.GQL.resolver()
        query_str = resolver.make_add_mutation_str(include_upsert=upsert is not None)
        variables = {"input": jsonable_encoder(inputs)}
        if upsert is not None:
            variables["upsert"] = upsert
        j = await cls.GQL.dgraph_client.execute(
            query_str=query_str, variables=variables, use_one_time=True
        )
        node_d_lst = j["data"][f"{cls.GQL.add_function_name}"][
            cls.GQL.payload_node_name
        ]
        return [resolver.parse_obj_nested(node_d) for node_d in node_d_lst]

    @staticmethod
    def make_gql_d_from_rel_d_input(rel_d_input: REL_D_INPUT) -> GQL_D:
        """
        takes {taught_by: Teacher, is_friends_with: T.List[Student]} ->
        {taught_by: {id: 0x1}, is_friends_with: [{id: 0x2, id: 0x3}] }}
        """
        gql_d_output: GQL_D = {}
        for field_name, node_or_nodes in rel_d_input.items():
            if node_or_nodes is None:
                continue
            if type(node_or_nodes) in [set, list, tuple]:
                val = {n._uid_field_name: n._uid for n in node_or_nodes}
            else:
                node_or_nodes: NodeModel
                val = {node_or_nodes._uid_field_name: node_or_nodes._uid}
            gql_d_output[field_name] = val
        return gql_d_output

    @staticmethod
    def objs_to_str(obj_d: T.Dict[str, T.Any]) -> T.Dict[str, T.Any]:
        if not obj_d:
            return obj_d
        cleaned_set_d = {}
        for key, val in obj_d.items():
            if isinstance(val, BaseModel):
                val = val.json()
            if type(val) is dict:
                val = json.dumps(val)
            cleaned_set_d[key] = val
        return cleaned_set_d

    async def _update(
        self,
        *,
        given_resolver: T.Optional[ResolverType] = None,
        to_set: T.Optional[REL_D_INPUT] = None,
        to_remove: T.Optional[REL_D_INPUT] = None,
        print_update_d: bool = False,
    ) -> bool:
        set_d, remove_d = self.base_set_remove_d(to_set=to_set, to_remove=to_remove)
        # turn base models or dicts into strs
        """i moved the functions below to inside the function above. This is because relationships should 
        not be turned to string, but nested values should be"""
        # set_d = self.objs_to_str(set_d)
        # remove_d = self.objs_to_str(remove_d)
        return await self.update_from_set_remove_ds(
            set_d=set_d,
            remove_d=remove_d,
            given_resolver=given_resolver,
            print_update_d=print_update_d,
        )

    async def update_from_set_remove_ds(
        self,
        *,
        given_resolver: T.Optional[ResolverType] = None,
        set_d: GQL_D,
        remove_d: GQL_D,
        print_update_d: bool = False,
    ) -> bool:
        """In future, use args from actual update func from gql.schema"""
        if not set_d and not remove_d:
            print("NOTHING TO UPDATE!")
            return False

        variables = {
            "set": jsonable_encoder(set_d),
            "remove": jsonable_encoder(remove_d),
            "filter": {self._uid_field_name: self._uid},
        }

        if print_update_d:
            debug(variables)

        resolver = given_resolver or self._used_resolver
        query_str = resolver.make_update_mutation_str()
        j = await self.GQL.dgraph_client.execute(
            query_str=query_str, variables=variables
        )
        node_d_lst = j["data"][f"{self.GQL.update_function_name}"][
            self.GQL.payload_node_name
        ]
        if not node_d_lst:
            # raise Exception("No update was registered!!")
            print("NO UPDATE WAS REGISTERED")
            return False

        node_d = node_d_lst[0]
        new_node = resolver.parse_obj_nested(node_d)
        self.hydrate(new_node=new_node)

        return True

    async def delete(self, given_resolver: ResolverType = None) -> bool:
        """In future, use actual GQL.schema"""
        if not self.GQL.delete_function_name:
            raise GQLException(f"No delete function given for {self.GQL.typename}")
        resolver = given_resolver or self._used_resolver
        query_str = resolver.make_delete_mutation_str()
        variables = {"filter": {self._uid_field_name: self._uid}}
        j = await self.GQL.dgraph_client.execute(
            query_str=query_str, variables=variables
        )
        node_d_lst = j["data"][f"{self.GQL.delete_function_name}"][
            self.GQL.payload_node_name
        ]
        if not node_d_lst:
            # raise Exception("No update was registered!!")
            print("NO DELETE WAS REGISTERED")
            return False
        node_d = node_d_lst[0]
        node = resolver.parse_obj_nested(node_d)
        node._deleted = True
        self.hydrate(new_node=node)
        return True

    @classmethod
    async def delete_many(
        cls: T.Type[NodeModel],
        *,
        nodes: T.List[NodeModel],
        given_resolver: ResolverType = None,
    ) -> bool:
        if not cls.GQL.delete_function_name:
            raise GQLException(f"No delete function given for {cls.GQL.typename}")
        resolver = given_resolver or cls.GQL.resolver()
        query_str = resolver.make_delete_mutation_str()
        variables = {
            "filter": {cls.GQL.uid_field_name: [node._uid for node in nodes]},
        }
        j = await cls.GQL.dgraph_client.execute(
            query_str=query_str, variables=variables
        )
        node_d_lst = j["data"][f"{cls.GQL.delete_function_name}"][
            cls.GQL.payload_node_name
        ]
        if not node_d_lst:
            # raise Exception("No update was registered!!")
            print("NO DELETE WAS REGISTERED")
            return False

        for og_node, node_d in zip(nodes, node_d_lst):
            new_node = resolver.parse_obj_nested(node_d)
            new_node._deleted = True
            og_node.hydrate(new_node=new_node)
        return True


from .resolver import Resolver

Cache.update_forward_refs()
