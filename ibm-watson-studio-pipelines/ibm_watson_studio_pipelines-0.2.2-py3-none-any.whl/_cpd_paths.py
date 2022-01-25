# Copyright IBM Corp. 2021. All Rights Reserved.

import re
from abc import abstractmethod
from typing import Optional, Tuple, Set, Type, Mapping, Sequence, TypeVar

from abc import ABC
from attr import attrs, evolve
import urllib.parse


_segment_regex: re.Pattern = re.compile(r'[a-zA-Z0-9:._+-~]*')
_segment_allowed_characters: Set[str] = set(':._+-~')

Self = TypeVar('Self')

def _validate_segment(segment: str) -> None:
    if _segment_regex.fullmatch(segment):
        return

    forbidden_chars = set()
    for ch in segment:
        if ch in forbidden_chars:
            continue
        if not _segment_regex.fullmatch(ch):
            forbidden_chars.add(ch)

    forbidden_chars_str = ', '.join([f"'{ch}'" for ch in forbidden_chars])
    raise TypeError(f"segment '{segment}' contains forbidden characters: {forbidden_chars_str}")

class CpdPath(ABC):
    @abstractmethod
    def __str__(self) -> str: ...

    @classmethod
    @abstractmethod
    def from_string(cls: Type[Self], s: str) -> Self: ...

    @classmethod
    def try_from_string(cls: Type[Self], s: str) -> Optional[Self]:
        # noinspection PyBroadException
        try:
            return cls.from_string(s)
        except Exception:
            return None

@attrs(auto_attribs=True, frozen=True)
class CpdQuery:
    params: Mapping[str, Sequence[str]]

    @classmethod
    def from_string(cls: Type[Self], s: str) -> Self:
        if len(s) != 0 and s[0] == '?':
            s = s[1:]
        query_params = urllib.parse.parse_qs(s)
        return cls(query_params)

    def __str__(self) -> str:
        return urllib.parse.urlencode(self.params)

class CpdPathCanonical(CpdPath, ABC):
    @abstractmethod
    def resource_id(self) -> str: ...

class CpdPathQuery(CpdPath, ABC):
    @abstractmethod
    def query(self) -> str: ...


@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPathToScope(CpdPath, ABC):
    """Any path to scope."""
    has_prefix: bool
    context: Optional[str]
    scope_type: str

    def _prefix_to_str(self) -> str:
        result = f"{self.context or ''}/{self.scope_type}"
        if self.has_prefix:
            result = "cpd://" + result
        return result

    @classmethod
    def try_from_string_prefix(cls: Type[Self], s: str) -> Tuple[Optional[Self], str]:
        s = s.strip()
        result = urllib.parse.urlparse(s)
        if result.scheme == 'cpd' or (result.scheme == '' and result.path.startswith('/')):
            return cls._from_parse_result(result)
        else:
            return None, s

    @classmethod
    def from_string(cls: Type[Self], s: str) -> Self:
        result = urllib.parse.urlparse(s)
        return cls._from_parse_result(result)[0]

    @classmethod
    def _from_parse_result(cls, result: urllib.parse) -> Tuple['CpdPathToScope', str]:
        has_prefix = False
        if result.scheme == 'cpd':
            has_prefix = True

        context = result.netloc
        if context == '':
            context = None

        query = result.query
        if query == '':
            query = None

        parts = result.path.split("/")
        if parts[0] == '':
            del parts[0]

        if len(parts) == 2 and query is not None:
            raise TypeError(f"Canonical CPD path to a scope '{parts[1]}' has query: {parts}")

        for part in parts:
            _validate_segment(part)

        scope_type = parts[0]
        scope_id = parts[1] if len(parts) >= 2 else None
        other_parts = parts[2:] if len(parts) >= 2 else []

        scope_types = [
            "projects",
            "spaces",
            "catalogs",
        ]

        if scope_type not in scope_types:
            raise TypeError(f"Unknown scope type: '{scope_type}'")

        if len(parts) == 1:
            # query path?
            if query is None:
                raise TypeError(f"Canonical path must have id. Query path must have query. Lacking either.")

            return CpdScopeQuery(
                has_prefix=has_prefix,
                context=context,
                scope_type=scope_type,
                query_data=CpdQuery.from_string(query),
            ), ""
        # maybe file?
        elif len(parts) >= 3 and parts[2] == 'files':
            return CpdScopeFile(
                has_prefix = has_prefix,
                context = context,
                scope_type = scope_type,
                scope_id = scope_id,
                file_path = "/" + "/".join(parts[3:])
            ), ""
        else:
            remaining = "/".join(other_parts)
            if len(other_parts) > 0 and query is not None:
                remaining += '?' + query

            return CpdScope(
                has_prefix = has_prefix,
                context = context,
                scope_type = scope_type,
                scope_id = scope_id,
            ), remaining

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdScope(CpdPathToScope, CpdPathCanonical):
    """Canonical path to a scope."""
    scope_id: str

    def __str__(self) -> str:
        return self._prefix_to_str() + '/' + self.scope_id

    def resource_id(self) -> str:
        return self.scope_id

    @classmethod
    def from_string(cls: Type[Self], s: str) -> Self:
        result = super(cls).from_string(s)
        if not isinstance(result, cls):
            raise TypeError("Not a canonical path. Query present.")
        return result

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdScopeQuery(CpdPathToScope, CpdPathQuery):
    """Querying path to a scope."""
    query_data: CpdQuery

    def __str__(self) -> str:
        return self._prefix_to_str() + '?' + str(self.query)

    def query(self) -> str:
        return str(self.query_data)

    @classmethod
    def from_string(cls: Type[Self], s: str) -> Self:
        result = super(cls).from_string(s)
        if not isinstance(result, cls):
            raise TypeError("Not a querying path. No query present.")
        return result

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPathToFile(CpdPath, ABC):
    """CPD path pointing at a file inside of some file container."""
    file_path: str

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdScopeFile(CpdScope, CpdPathToFile):
    """CPD path pointing at a file in a scope (space or project)."""
    def __str__(self) -> str:
        file_path = self.file_path
        if len(file_path) == 0 or file_path[0] != '/':
            file_path = '/' + file_path
        return CpdPathToFile.__str__(self) + "/files" + file_path


@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPathResource(CpdPath, ABC):
    """CPD path to some resource in scope."""
    scope: Optional[CpdScope]
    resource_type: str

    def __str__(self) -> str:
        return str(self.scope) + "/" + self.resource_type

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPathResourceCanonical(CpdPathCanonical, CpdPathResource, ABC):
    _resource_id: str

    def resource_id(self) -> str:
        return self._resource_id

    def __str__(self):


@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPath:
    scope: Optional[CpdScope]
    path: str
    query: Optional[str] = None

    def __str__(self) -> str:
        result = []
        if self.scope is not None:
            result.append(str(self.scope))
        if self.path != '':
            result.append(self.path)
        result_str = "/".join(result)
        if self.query is not None:
            result_str += '?' + self.query
        return result_str

    @classmethod
    def from_string(cls, s: str) -> 'CpdPath':
        s = s.strip()
        scope, s = CpdScope.try_from_string(s)

        result = urllib.parse.urlparse(s)
        path = result.path
        parts = path.split("/")

        for part in parts:
            _validate_segment(part)

        query = result.query
        if query == '':
            query = None

        # if no scope, an additional case of "just by-id asset" must be checked
        if scope is None:
            if path.find("/") == -1: # no slashes --- it is by-id asset
                path = f"assets/{path}"

        if path.count("?") > 0:
            raise TypeError("Question mark can only be used once.")

        # what kind of path is it?
        if len(parts) > 3 and parts[0] == 'connections' and parts[2] == 'files':
            result = CpdPathToConnectionFile(scope=scope, path=path, query=query)
        else:
            result = CpdPath(scope=scope, path=path, query=query)
        return result

    def resource_id(self) -> Optional[str]:
        if self.query is not None:
            # if query is defined, cpd_path is not pointing at a specific
            # resource_id but instead, it searches using that query
            return None
        # otherwise, it's the last part of path
        return self.path.split('/')[-1]

    def is_relative(self) -> bool:
        return self.scope is None

    def resolve_at(self, cpd_scope: CpdScope) -> 'CpdPath':
        if self.scope is not None:
            return evolve(self)
        return evolve(self, scope=cpd_scope)

@attrs(auto_attribs=True, frozen=True, kw_only=True)
class CpdPathToConnectionFile(CpdPath):
    """CPD path pointing at a file inside some connection"""

    def resource_id(self) -> Optional[str]:
        return self.path.split('/')[1]

    def bucket_name(self) -> str:
        return self.path.split('/')[3]

    def file_path(self) -> str:
        return '/' + '/'.join(self.path.split('/')[4:])