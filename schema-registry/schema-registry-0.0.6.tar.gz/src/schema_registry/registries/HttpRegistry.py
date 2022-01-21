from functools import lru_cache
import json
from typing import Any, Dict, List, Optional, Set

from requests_toolbelt.sessions import BaseUrlSession
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from schema_registry.config import get_logger
from schema_registry.registries.entities import EnrichedNamespace, VersionedType


class HttpSchemaRegistry:
    def __init__(self, *, url: str) -> None:
        self.url = url
        self.session = BaseUrlSession(base_url=self.url)
        self.log = get_logger(self.__class__.__name__)
        self._namespaces: Set[str] = set()
        self._types: Dict[str, Set[VersionedType]] = {}

    @lru_cache(maxsize=128)
    def get(
        self, *, namespace: str, type_name: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        if version is None:
            version = self.find_latest_version(namespace=namespace, type_name=type_name)

        req = self.session.get(
            f"/registry/{namespace}/{type_name}/{version}/schema.json"
        )

        self.log.debug(req)
        if req.status_code != 200:
            return None
        return req.json()  # type: ignore

    @property
    def namespaces(self) -> Set[str]:
        if not self._namespaces:
            self._initialize_namespaces()
        return self._namespaces

    def types(self, *, namespace: str) -> Set[VersionedType]:
        preliminary_result = self._types.get(namespace)

        if preliminary_result is None:
            self.log.debug(f"Fetching types for {namespace} from remote")
            self._initialize_types(namespace)

        return self._types.get(namespace, set())

    def _initialize_namespaces(self) -> None:
        index = self.session.get("/registry/index.json").json()
        schemes = index.get("schemes", [])

        self.log.debug(schemes)

        self._namespaces = {schema["ns"] for schema in schemes}

    def _initialize_types(self, namespace: str) -> None:
        index = self.session.get("/registry/index.json").json()
        schemes = index.get("schemes", [])
        filtered = filter(lambda x: x["ns"] == namespace, schemes)

        self._types[namespace] = {
            VersionedType(name=schema["type"], version=schema["version"])
            for schema in filtered
        }

    def find_latest_version(self, *, namespace: str, type_name: str) -> int:
        self.log.debug("Fetching version")
        types_of_namespace = self.types(namespace=namespace)

        found_types = list(filter(lambda x: x.name == type_name, types_of_namespace))
        found_types.sort()

        self.log.debug(f"Found {found_types}")

        # TODO: deal with case where found_types is empty/None
        version = found_types[-1].version

        if len(found_types) != 1:
            self.log.info(
                f"Found {len(found_types)} versions using latest version ({version})"
            )

        return version

    def refresh(self) -> None:
        self._initialize_namespaces()
        self._types = {}
        self.get.cache_clear()

    # TODO Transformation stuff


class EnrichingHttpSchemaRegistry:
    def __init__(self, *, url: str) -> None:
        self.url = url
        self.session = BaseUrlSession(base_url=self.url)
        self.http_schema_registry = HttpSchemaRegistry(url=url)
        self.log = get_logger(self.__class__.__name__)
        self._namespaces: Set[EnrichedNamespace] = set()
        self._types: Dict[str, Set[VersionedType]] = {}

    @lru_cache(maxsize=128)
    def get(
        self, *, namespace: str, type_name: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        if version is None:
            version = self.http_schema_registry.find_latest_version(
                namespace=namespace, type_name=type_name
            )

        schema = None

        try:
            schema_code, _ = self._get_code_elements(
                namespace=namespace, type_name=type_name, version=version
            )  # type: ignore
            schema_description = self._get_schema_description(
                namespace=namespace, type_name=type_name
            )
            schema = json.loads(schema_code.get_text())
            schema["title"] = "\n".join(schema_description)

            self.log.debug(f"Found schema: {schema}")
        except TypeError:
            self.log.info("Requested schema not found.")
        except json.JSONDecodeError:
            self.log.warning(
                "Could not translate remote schema into JSON. HTML parsing or the page might be off."
            )

        return schema

    def _get_code_elements(
        self, *, namespace: str, type_name: str, version: int
    ) -> Optional[ResultSet]:

        # The way this is currently written is that 2 requests are made if the example and
        # the schema for the same event are requested. This is based on the assumption,
        # that users are interested in one or the other but not frequently in both.
        # Therefore trading of network traffic vs memory footprint.
        # * Should this prove false, we want lru_caching here as well, or maybe even
        # * a more powerful caching mechanism

        req = self.session.get(f"/{namespace}/{type_name.lower()}/{version}/index.html")

        if req.status_code != 200:
            return None

        raw_schema_html = req.content
        schema_html = BeautifulSoup(raw_schema_html, features="lxml")
        code_elements = schema_html.find_all("code")

        self.log.debug(f"Found {len(code_elements)} code elements")
        if len(code_elements) != 2:
            raise AttributeError("More than 2 code elements found can not parse schema")

        return code_elements

    def _get_schema_description(self, namespace: str, type_name: str) -> List[str]:
        req = self.session.get(f"/{namespace}/{type_name.lower()}/index.html")

        raw_schema_html = req.content
        schema_html = BeautifulSoup(raw_schema_html, features="lxml")
        headline = schema_html.body.h1

        description = []
        next_sibling = headline.next_sibling
        while next_sibling.name != "h2":
            self.log.debug(f"Sibling: {next_sibling}: {next_sibling.name}")
            if next_sibling.string and next_sibling.string.strip():
                description.append(next_sibling.string.strip())
            next_sibling = next_sibling.next_sibling

        return description

    @lru_cache(maxsize=128)
    def example(
        self, *, namespace: str, type_name: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        if version is None:
            version = self.http_schema_registry.find_latest_version(
                namespace=namespace, type_name=type_name
            )

        example = None

        try:
            _, example_code = self._get_code_elements(
                namespace=namespace, type_name=type_name, version=version
            )  # type: ignore
            example = json.loads(example_code.get_text())

            self.log.debug(f"Found example: {example}")
        except TypeError:
            self.log.info("Requested example not found.")
        except json.JSONDecodeError:
            self.log.warning(
                "Could not translate remote example into JSON. HTML parsing or the page might be off."
            )

        return example

    @property
    def namespaces(self) -> Set[EnrichedNamespace]:
        if not self._namespaces:
            self._initialize_namespaces()
        return self._namespaces

    def _initialize_namespaces(self) -> None:
        namespaces = self.http_schema_registry.namespaces
        self._namespaces = set()
        for namespace in namespaces:
            req = self.session.get(f"/{namespace}")
            raw_schema_html = req.content
            namespace_html = BeautifulSoup(raw_schema_html, features="lxml")
            description = namespace_html.find("div", {"id": "body-inner"}).p

            if description and description.string:
                title = description.string
            else:
                title = ""

            self._namespaces.add(EnrichedNamespace(name=namespace, title=title))

    def types(self, *, namespace: str) -> Set[VersionedType]:
        return self.http_schema_registry.types(namespace=namespace)

    def refresh(self) -> None:
        self.http_schema_registry.refresh()
        self.get.cache_clear()

    # TODO Transformation stuff
