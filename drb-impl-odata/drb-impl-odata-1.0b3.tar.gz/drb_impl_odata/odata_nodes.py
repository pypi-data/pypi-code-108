from __future__ import annotations

import uuid
import io
from drb import DrbNode
from drb.path import ParsedPath
from drb.predicat import Predicate
from drb.exceptions import DrbException
from requests.auth import AuthBase
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from .odata_node import OdataNode
from .odata_utils import req_svc_products, req_product_by_uuid, req_svc_count,\
    req_product_download, req_product_attributes, ODataQueryPredicate
from .exceptions import OdataRequestException


class ODataServiceNode(OdataNode):
    def __init__(self, url: str, auth: AuthBase = None):
        super(ODataServiceNode, self).__init__(url, auth)
        self.__path = ParsedPath(url)

    @property
    def name(self) -> str:
        return self._service_url

    @property
    def namespace_uri(self) -> Optional[str]:
        return 'OData.CSC'

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    @property
    def children(self) -> List[DrbNode]:
        return ProductList(self)

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException('ODataNode has no attribute')

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is not None:
                return len(req_svc_products(
                    self, filter=f"Name eq '{name}'")) > 0
            return req_svc_count(self) > 0
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f"ODataNot doesn't support {impl} implementation")

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0)\
            -> Union[DrbNode, List[DrbNode]]:
        if namespace_uri is None:
            products = req_svc_products(self, filter=f"Name eq '{name}'")
            if len(products) <= 0:
                raise DrbException(f'No child ({name}, {namespace_uri},'
                                   f' {occurrence}) found')
            p = products[occurrence]
            if isinstance(p, list):
                return [ODataProductNode(self, x['Id'], data=x) for x in p]
            return ODataProductNode(self, p['Id'], data=p)
        raise DrbException(f'No child ({name}, {namespace_uri}, {occurrence}) '
                           'found')

    def __retrieve_child_from_tuple(self, t: tuple) -> \
            Union[List[DrbNode], DrbNode]:
        if len(t) == 2:
            # (name, namespace)
            if t[1] is None or isinstance(t[1], str):
                return self._get_named_child(name=t[0], namespace_uri=t[1])
            # (name, occurrence)
            elif isinstance(t[1], int) or isinstance(t[1], slice):
                return self._get_named_child(t[0], occurrence=t[1])
        # (name, namespace, occurrence)
        elif len(t) == 3:
            return self._get_named_child(*t)
        raise KeyError(f'Invalid key: {t}')

    def __retrieve_child(self, key: Union[uuid.UUID, tuple, Predicate]) -> \
            Union[List[DrbNode], DrbNode]:
        try:
            if isinstance(key, uuid.UUID):
                prd_uuid = str(key)
                data = req_product_by_uuid(self, prd_uuid)
                return ODataProductNode(self, str(prd_uuid), data=data)
            if isinstance(key, tuple):
                return self.__retrieve_child_from_tuple(key)
            if isinstance(key, str):
                return self._get_named_child(key)
            if isinstance(key, ODataQueryPredicate):
                return [ODataProductNode(self, p['Id'], data=p)
                        for p in key.apply_query(self)]
        except DrbException as ex:
            raise KeyError from ex
        raise TypeError('Invalid type for a DrbNode bracket: '
                        f'{key.__class__}')

    def __len__(self):
        return req_svc_count(self)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.children[item]
        return self.__retrieve_child(item)

    def __truediv__(self, other):
        return self.__retrieve_child(other)


class ProductList(list):
    """
    Specific read only list to access to OData CSC Product entities:
     * Any access generate a remote access to the associated OData service
     * Any inherited functions allowing to modify the list have no effect.
     * comparator functions are not supported except the equal comparator.
    """

    def __init__(self, odata: ODataServiceNode):
        super().__init__()
        self.__odata = odata

    def __getitem__(self, item):
        count = req_svc_count(self.__odata)
        if isinstance(item, int):
            if -count < item >= count:
                raise IndexError
            if item >= 0:
                skip = item
            else:
                skip = item + count
            products = req_svc_products(self.__odata, skip=skip, top=1)
            prd = products[0]
            prd_uuid = products[0]['Id']
            return ODataProductNode(self.__odata, prd_uuid, data=prd)
        if isinstance(item, slice):
            products = req_svc_products(self.__odata, skip=item.start,
                                        top=item.stop)
            return [ODataProductNode(self.__odata, p['Id'], data=p)
                    for p in products]
        raise TypeError

    def __iter__(self):
        def iterator():
            for index in range(0, len(self)):
                p = req_svc_products(self.__odata, skip=index, top=1)
                yield ODataProductNode(self.__odata, p[0]['Id'], data=p[0])

        return iterator()

    def __len__(self):
        return req_svc_count(self.__odata)

    def __sizeof__(self):
        super().__sizeof__()

    def append(self, obj: Any) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def copy(self) -> List[ODataProductNode]:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def extend(self, iterable: Iterable[ODataProductNode]) -> None:
        raise NotImplementedError

    def index(self, value: Any, start: int = ..., stop: int = ...) -> int:
        raise NotImplementedError

    def insert(self, index: int, obj: ODataProductNode) -> None:
        raise NotImplementedError

    def pop(self, index: int = ...) -> ODataProductNode:
        raise NotImplementedError

    def remove(self, value: Any) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        raise NotImplementedError

    def sort(self: List, *, key: None = ..., reverse: bool = ...) -> None:
        raise NotImplementedError


class ODataProductNode(OdataNode):
    def __init__(self, source: Union[str, OdataNode], product_uuid: str,
                 **kwargs):
        if isinstance(source, OdataNode):
            super(ODataProductNode, self).__init__(source.get_service_url(),
                                                   source.get_auth())
            self.__parent = source
        else:
            auth = kwargs['auth'] if 'auth' in kwargs.keys() else None
            super(ODataProductNode, self).__init__(source, auth)
            self.__parent = None

        self.__uuid = product_uuid
        self.__path = ParsedPath(
            f'{self.get_service_url()}/Products({self.__uuid})')
        self.__product = kwargs['data'] if 'data' in kwargs.keys() else None
        self.__attr = None

    def __load_product(self):
        if self.__product is None:
            self.__product = req_product_by_uuid(self, self.__uuid)

    @property
    def name(self) -> str:
        self.__load_product()
        return self.__product['Name']

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.__parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        self.__load_product()
        return {(k, None): v for k, v in self.__product.items()}

    @property
    def children(self) -> List[DrbNode]:
        return [ODataProductAttributeNode(self, self.__uuid)]

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        self.__load_product()
        if namespace_uri is None:
            try:
                return self.__product[name]
            except KeyError:
                pass
        raise DrbException(f'No attribute found: ({name}, {namespace_uri})')

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is not None:
                return name == self.children[0].name
            return True
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        online = self.get_attribute('Online')
        return online and (impl == io.BufferedIOBase or impl == io.BytesIO)

    def get_impl(self, impl: type, **kwargs) -> Any:
        if self.has_impl(impl):
            return req_product_download(self, self.__uuid)
        raise DrbException(f'Not supported implementation: {impl}')

    def __eq__(self, other):
        if isinstance(other, ODataProductNode):
            return super().__eq__(other) and other.__uuid == self.__uuid
        return False

    def __hash__(self):
        return hash(self._service_url)


class ODataProductAttributeNode(OdataNode):
    __name = 'Attributes'

    def __init__(self, source: ODataProductNode, prd_uuid: str):
        super().__init__(source.get_service_url(), source.get_auth())
        self.__uuid = prd_uuid
        self.__parent = source
        self.__attr = None

    def __load_attributes(self) -> None:
        if self.__attr is None:
            self.__attr = req_product_attributes(self, self.__uuid)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def path(self) -> ParsedPath:
        return self.__parent.path / self.__name

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.__parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    @property
    def children(self) -> List[DrbNode]:
        self.__load_attributes()
        return [ODataAttributeNode(self, data=x) for x in self.__attr]

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'No attribute found: ({name}, {namespace_uri})')

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is not None:
                for x in self.__attr:
                    if name in x.keys():
                        return True
                return False
            return len(self.__attr) > 0
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f'Do not support implementation: {impl}')


class ODataAttributeNode(OdataNode):
    def __init__(self, source: Union[str, ODataProductAttributeNode],
                 **kwargs):
        if isinstance(source, ODataProductAttributeNode):
            super().__init__(source.get_service_url(), source.get_auth())
            self.__parent = source
        elif isinstance(source, str):
            auth = kwargs['auth'] if 'auth' in kwargs.keys() else None
            super().__init__(source, auth)
            self.__parent = None
        else:
            raise OdataRequestException(f'Unsupported source: {type(source)}')
        self.__path = None
        self.__data = kwargs['data'] if 'data' in kwargs.keys() else None

    @property
    def name(self) -> str:
        return self.__data['Name']

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return self.__data['Value']

    @property
    def path(self) -> ParsedPath:
        if self.__path is None:
            if self.__parent is None:
                self.__path = ParsedPath(self.name)
            else:
                self.__path = self.__parent.path / self.name
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.__parent

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {(k, None): v for k, v in self.__data.items()}

    @property
    def children(self) -> List[DrbNode]:
        return []

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        if namespace_uri is None and name in self.__data.keys():
            return self.__data[name]
        raise DrbException(f'Attribute not found: ({name}, {namespace_uri})')

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f'Do not support implementation: {impl}')
