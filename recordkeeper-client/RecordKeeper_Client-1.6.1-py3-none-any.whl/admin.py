import ast
import json
import logging
from uuid import UUID
from typing import Tuple, List, Optional, Any, Callable, Dict

from rkclient.entities import Artifact, PEM
from rkclient.client import RKClient
from rkclient.serialization import ArtifactSerialization, PEMSerialization, _decode_from_base64

log = logging.getLogger("rkclient")


class RKAdmin(RKClient):
    """
    This class is not supposed to be used by normal RK user, but by RK administrator or in tests.
    """

    def clean_dbs(self) -> Tuple[str, bool]:
        """
        :return: first element: error message or 'OK'
                 second element: True for success, False for error
        """
        text, ok = self._post("/clean", "{}")
        if not ok:
            return f"Cleaning db failed: {text}", False
        return 'OK', True

    def get_pems(self,
                 page_index: int = -1,
                 page_size: int = -1,
                 sort_field: str = '',
                 sort_order: str = '',
                 filters: Optional[Dict] = None) -> Tuple[List[PEM], str, bool]:
        """
        :return: first element: list of pems (as json string) or error message
                 The artifacts lists in PEM will contain only artifact ID
                 second element: True for success, False for error
        """
        def _get_pems() -> Tuple[List[Any], str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            text, ok = self._get("/pems", query_params)
            if not ok:
                return [], text, False
            pems = []
            pems_json = json.loads(text)
            for p in pems_json:
                pems.append(PEMSerialization.from_dict(p, True))
            return pems, 'OK', True

        return _handle_request(_get_pems, "Getting pems")

    def get_pems_count(self,
                       page_index: int = -1,
                       page_size: int = -1,
                       sort_field: str = '',
                       sort_order: str = '',
                       filters: Optional[Dict] = None) -> Tuple[int, str, bool]:

        def _get_pems() -> Tuple[int, str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            text, ok = self._get("/pems_count", query_params)
            if not ok:
                return -1, text, False
            obj = json.loads(text)
            return int(obj['pems_count']), 'OK', True

        return _handle_request(_get_pems, "Getting pems count")

    def get_artifact(self, artifact_id: UUID, source: str = 'sqldb') -> Tuple[Optional[Artifact], bool]:
        # todo this could be improved by using different endpoint
        res, text, ok = self.get_artifacts(source)
        if not ok:
            log.error(f"Getting artifact failed: {text}")
            return None, False

        artifacts: List[Artifact] = res
        for a in artifacts:
            if a.ID == artifact_id:
                return a, True

        return None, False

    def get_artifacts(self,
                      source: str = 'sqldb',
                      page_index: int = -1,
                      page_size: int = -1,
                      sort_field: str = '',
                      sort_order: str = '',
                      filters: Optional[Dict] = None ) -> Tuple[List[Artifact], str, bool]:
        """
        :param source: from which db to return artifacts, 'sqldb' or 'graphdb'
        :param page_index:
        :param page_size:
        :param sort_field:
        :param sort_order:
        :param filters: contains dict of key:value pairs, which all has to be contained in artifact to be returned
        :return: first element: list of artifact objs. Artifacts contain also the taxonomies ids and xml content.
                 second element: optional str error message
                 third element: True for success, False for error
        """
        if source == 'sqldb':
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(page_index, page_size,
                                                                           sort_field, sort_order, filters)
            return self._get_artifacts_from_sql(query_params)
        elif source == 'graphdb':
            return self._get_artifacts_from_graph()
        else:
            return [], f"Getting artifacts: didn't recognize source: {source}", False

    def get_artifacts_count(self,
                            source: str = 'sqldb',
                            filters: Optional[Dict] = None) -> Tuple[int, str, bool]:
        """
        :param source: from which db to return artifacts, currenntly only 'sqldb' supported
        :param filters: contains dict of key:value pairs, which all has to be contained in artifact to be counted
        :return: first element: count of artifact objs
                 second element: optional str error message
                 third element: True for success, False for error
        """
        def _get_artifacts_count_from_sql() -> Tuple[int, str, bool]:
            query_params: Dict[str, Any] = _parse_sorting_filtering_params(-1, -1, "", "", filters)
            text, ok = self._get("/artifacts_count", query_params)
            if not ok:
                return -1, text, False
            objs = json.loads(text)
            return int(objs['artifacts_count']), "", True

        if source == 'sqldb':
            return _handle_request(_get_artifacts_count_from_sql, 'Getting artifacts count')
        else:
            return -1, f"Getting artifacts count: didn't recognize source: {source}", False

    def get_taxonomy_file(self, taxonomy_id: UUID) -> Tuple[str, bool]:
        text, ok = self._get(f"/taxonomy/{taxonomy_id.hex}")
        if not ok:
            return f"Getting taxonomy file failed: {text}", False
        return _decode_from_base64(text), True

    def get_tags(self) -> Tuple[List[Dict], str, bool]:
        """
        :return: first element: list of metadata (as Dict), with fields: NamespaceID, Tag, EventID, UpdatedAt
                 second element: error message
                 third element: True for success, False for error
        """
        def _get_tags() -> Tuple[List[Any], str, bool]:
            text, ok = self._get("/tags")
            if not ok:
                return [], text, False
            tags = json.loads(text)
            return tags, 'OK', True

        return _handle_request(_get_tags, "Getting tags")

    def query_graph(self, query: str, query_type='rw') -> Tuple[str, bool]:
        """
        :return: first element: returned result (as str with format corresponding to what query requests) or error message
                 second element: True for success, False for error
        """
        query_fmt = f'"query": "{query}", "type": "{query_type}"'
        payload = '{' + query_fmt + '}'
        return self._post("/query", payload)

    def _get_artifacts_from_sql(self, query_params: Dict[str, Any]) -> Tuple[List[Artifact], str, bool]:
        text, ok = self._get("/artifacts", query_params)
        if not ok:
            return [], f"Querying SQL failed: {text}", False

        objs = json.loads(text)
        artifacts: List[Artifact] = [ArtifactSerialization.from_dict(o) for o in objs]
        return artifacts, "", True

    def _get_artifacts_from_graph(self) -> Tuple[List[Artifact], str, bool]:
        text, ok = self.query_graph('MATCH (a:Artifact) RETURN a.rk_id AS rk_id, a.type as rk_type')
        if not ok:
            return [], text, False

        # the text contains python like list [['<uuid>', '<type'>], ['<uuid>', '<type>']]
        objs = ast.literal_eval(text)
        artifacts: List[Artifact] = [
            ArtifactSerialization.from_dict(
                {'ID': o[0], 'Type': o[1], 'Properties': {}, 'CreatedAt': None, 'TaxonomyFiles': None}
            )
            for o in objs
        ]
        return artifacts, "", True


def _handle_request(func: Callable, name: str) -> Tuple[Any, str, bool]:
    """
    Wraps the error, logging and exception handling.
    """
    obj, text, ok = func()
    if not ok:
        text = f"{name} failed: {text}"
        log.error(text)
        return "", text, False
    return obj, 'OK', True


def _parse_sorting_filtering_params(
        page_index: int = -1,
        page_size: int = -1,
        sort_field: str = '',
        sort_order: str = '',
        filters: Optional[Dict] = None) -> Dict[str, Any]:

    if filters is None:
        filters = {}
    params: Dict[str, Any] = {}
    if page_index != -1:
        params['pageIndex'] = page_index
    if page_size != -1:
        params['pageSize'] = page_size
    if sort_field != '':
        params['sortField'] = sort_field
    if sort_order != '':
        params['sortOrder'] = sort_order

    for key, value in filters.items():
        params[key] = value
    return params
