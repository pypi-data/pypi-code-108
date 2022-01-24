import copy
import json
import math
from abc import ABC
from concurrent import futures
import asyncio
import aiohttp
from logging import getLogger
from typing import Dict, List, TypeVar, Type, Union, Optional, Tuple

import tqdm
import urllib3
from aiologger.levels import LogLevel
from coloredlogs import ColoredFormatter
from pydantic.json import pydantic_encoder
from requests import Session, Response
from requests_futures.sessions import FuturesSession
from aiologger import Logger
from rallycli.errors import RallyError, requests_error_handling, rally_raise_errors
from rallycli.models import RallyTypeGeneric

## logger definition
logger = getLogger(__name__)
## async logger
cfrm = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
aiologger = Logger.with_default_handlers(name=__name__, level=LogLevel.INFO)

## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()

T = TypeVar('T')
TRallyTypeGeneric = TypeVar("TRallyTypeGeneric", bound="RallyTypeGeneric")


# noinspection PyProtectedMember
class BaseAPI(ABC):
    _security_key: str = ""
    WSAPI_PATH: str = "slm/webservice/v2.0/"
    LBAPI_PATH: str = "analytics/v2.0/service/rally/workspace/"
    DEF_BASEURL: str = "https://eu1.rallydev.com/slm/webservice/v2.0/"

    CREATE_URL: str = "create"
    QUERY_URL: str = "query"
    UPDATE_URL: str = "update"
    DELETE_URL: str = "delete"

    def __init__(self,
                 session: Session,
                 baseurl: str,
                 workspace: str,
                 rally_api):
        self._rally_session = session
        if not baseurl:
            logger.warning(f"baseurl NOT set falling back to: {BaseAPI.DEF_BASEURL}")
        self._baseurl: str = self.__format_baseurl(baseurl if baseurl else BaseAPI.DEF_BASEURL)

        self._workspace = workspace
        self._rally_api = rally_api
        ## Base params will apply on every lowlevel query
        self._baseparams: dict = {
            "fetch": "true",
            "pagesize": 200,
            "projectScopeUp": "false",
            "projectScopeDown": "true"
        }
        if workspace:
            self._baseparams["workspace"] = workspace
        self._inner_apis: Dict[str, BaseAPI] = dict()
        # Other base params ...

    @staticmethod
    def __format_baseurl(candidate: str):
        logger.debug(f"Candidate : {candidate}")
        if BaseAPI.WSAPI_PATH in candidate.strip() or (BaseAPI.LBAPI_PATH in candidate.strip()):
            return candidate.strip()
        elif candidate.strip().endswith("/"):
            return f"{candidate.strip()}{BaseAPI.WSAPI_PATH}"
        else:
            return f"{candidate.strip()}/{BaseAPI.WSAPI_PATH}"

    def _url_from_type(self, rally_type: str, url_type: str, oid: str = None) -> str:
        url: str
        if url_type == BaseAPI.QUERY_URL:
            url = self._baseurl + rally_type + BaseAPI._security_key
        elif url_type == BaseAPI.CREATE_URL:
            url = f"{self._baseurl}{rally_type}/create{BaseAPI._security_key}"
        elif url_type in [BaseAPI.UPDATE_URL, BaseAPI.DELETE_URL] and oid:
            url = f"{self._baseurl}{rally_type}/{oid}"
        else:
            raise RallyError(f"Unable to get url from rally type: {rally_type} and url type {url_type}")
        return url

    @requests_error_handling
    def _set_security_key(self):
        """set security Token: Required for update/create/delete operations with BasicAuth
        Returns as '?key=xxxxxxxxxx' for convenient use
        """
        sec_resp: Response = self._rally_session.get(self._baseurl + "security/authorize")
        key: str = sec_resp.json()["OperationResult"]["SecurityToken"]
        rally_raise_errors(sec_resp)
        BaseAPI._security_key = f"?key={key}"
        logger.debug(f"setting security key: {self._baseurl}security/authorize --> {key}")

    def _get_api_instance(self, api_domain_class: Type[T], dict_key: str) -> T:
        if not issubclass(api_domain_class, BaseAPI):
            raise RallyError(f"Type {api_domain_class} is not a valid subclas of {BaseAPI}")
        if not self._inner_apis.get(dict_key):
            obj: api_domain_class = api_domain_class.__new__(api_domain_class)
            obj.__init__(self._rally_session,
                         self._baseurl,
                         self._workspace,
                         self._rally_api)
            self._inner_apis[dict_key] = obj
        return self._inner_apis[dict_key]

    @requests_error_handling
    def _post(self, url: str, data: dict, params: dict = None) -> dict:
        response = self._rally_session.post(url, data=json.dumps(data, default=pydantic_encoder), params=params)
        rally_raise_errors(response)
        if response.json().get("OperationResult") and response.json().get("OperationResult").get("Object"):
            return response.json()["OperationResult"]["Object"]  # udpate/delete
        elif response.json().get("OperationResult") and response.json().get("OperationResult").get("Results"):
            return response.json()["OperationResult"]["Results"]  # Collections
        elif response.json().get("CreateResult") and response.json().get("CreateResult").get("Object"):
            return response.json()["CreateResult"]["Object"]  # Create
        else:
            logger.debug(response.json())
            root_element_name = list(response.json().keys())[0]
            return response.json().get(root_element_name)

    async def _async_post(self, session: aiohttp.ClientSession, url: str, data: dict) -> dict:
        async with session.post(url, data=json.dumps(data, default=pydantic_encoder)) as response:
            jresults = await response.json(content_type=None)
            # logger.info(f"Post result ok: {response.ok}")
            response.raise_for_status()
            if jresults.get("OperationResult") and jresults.get("OperationResult").get("Object"):
                aiologger.debug(f"Updating {url}: {response.ok}")
                return jresults["OperationResult"]["Object"]  # udpate/delete
            elif jresults.get("OperationResult") and jresults.get("OperationResult").get("Results"):
                return jresults["OperationResult"]["Results"]  # Collections
            elif jresults.get("CreateResult") and jresults.get("CreateResult").get("Object"):
                aiologger.debug(f"Creating {url}: {jresults['CreateResult']['Object']['Name']}")
                return jresults["CreateResult"]["Object"]  # Create
            else:
                logger.debug(jresults)
                root_element_name = list(jresults.keys())[0]
                return jresults.get(root_element_name)

    @requests_error_handling
    async def _async_post_elements(self, url_data: List[Tuple[str, dict]]) -> List[dict]:
        headers = self._rally_session.headers
        tasks: List[asyncio.Task] = []
        async with aiohttp.ClientSession(headers=headers) as session:
            for t in url_data:
                url: str = t[0]
                data: dict = t[1]
                tasks.append(asyncio.create_task(self._async_post(session, url, data)))
            aiologger.info(f"Wainting (gather) for {len(tasks)}")
            result_list: List[dict] = await asyncio.gather(*tasks)

            return result_list

    @requests_error_handling
    def _get(self, url: str,
             params: dict,
             keys: List[str] = None,
             model_class: Type[T] = None) -> Union[Optional[Union[RallyTypeGeneric, T]],
                                                   List[Union[RallyTypeGeneric, T]]]:

        response = self._rally_session.get(url, params=params)
        rally_raise_errors(response)
        if model_class:
            rally_types: List[model_class] = []
        else:
            rally_types: List[RallyTypeGeneric] = []
        if response.json().get("QueryResult"):
            results = response.json()["QueryResult"]["Results"]
            for result in results:
                trimed_res = {key: result[key] for key in keys} if keys else result
                rally_types.append(self._get_rally_object(trimed_res, model_class=model_class))
            return rally_types
        else:
            root_element_name = list(response.json().keys())[0]
            result = response.json()[root_element_name]
            trimed_res = {key: result[key] for key in keys} if keys else result
            return self._get_rally_object(trimed_res, model_class=model_class)

    def _simple_query(self, params: dict, rally_type: str, keys: List[str],
                      model_class: Type[T] = None) -> List[Union[RallyTypeGeneric, T]]:
        url = self._url_from_type(rally_type, BaseAPI.QUERY_URL)
        results = self._get(url, params=params, keys=keys, model_class=model_class)
        return results

    def _create_from_model(self, model: TRallyTypeGeneric, rally_type: str) -> dict:
        url: str = self._url_from_type(rally_type, BaseAPI.CREATE_URL)
        ## set moodel Workspace
        model.Workspace = self._workspace
        logger.debug(url)
        data = {rally_type: model.dict()}
        created = self._post(url, data)
        return created

    def _update_from_model(self, model: TRallyTypeGeneric, rally_type: str) -> dict:
        url: str = f"{model._ref}{BaseAPI._security_key}"
        logger.debug(model)
        logger.debug(url)
        data = {rally_type: model}
        updated = self._post(url, data)
        return updated

    @requests_error_handling
    def _delete_from_model(self, model: TRallyTypeGeneric):
        url: str = f"{model._ref}{BaseAPI._security_key}"
        logger.debug(url)
        response = self._rally_session.delete(url)
        rally_raise_errors(response)

    def _add_members_refs_to_collection(self, parent_ref: str, collection_refs: List[str], collection_name: str):
        url: str = f"{parent_ref}/{collection_name}/add{BaseAPI._security_key}"
        ref_dicts: List[dict] = [{"_ref": ref} for ref in collection_refs]
        params = {
            "workspace": self._workspace
        }
        data = {
            "CollectionItems": ref_dicts
        }
        self._post(url, data, params=params)


    def _delete_members_refs_from_collection(self, parent_ref: str, collection_refs: List[str], collection_name: str):
        url: str = f"{parent_ref}/{collection_name}/remove{BaseAPI._security_key}"
        ref_dicts: List[dict] = [{"_ref": ref} for ref in collection_refs]
        params = {
            "workspace": self._workspace
        }
        data = {
            "CollectionItems": ref_dicts
        }
        self._post(url, data, params=params)

    def _add_new_members_to_collection(self, parent_ref: str,
                                       member_collection: List[TRallyTypeGeneric],
                                       collection_name: str):
        url: str = f"{parent_ref}/{collection_name}/add{BaseAPI._security_key}"
        data = {
            "CollectionItems": member_collection
        }
        self._post(url, data)

    @staticmethod
    def _get_rally_object_list(result_object_list: List[dict], model_class: Type[T]) -> List[T]:
        object_list: List[model_class] = []
        for result_object in result_object_list:
            obj = BaseAPI._get_rally_object(result_object, model_class=model_class)
            object_list.append(obj)
        return object_list

    @staticmethod
    def _get_rally_object(json_dict: dict, model_class: Type[T] = None) -> Union[T, RallyTypeGeneric]:
        if model_class:
            obj: T = model_class.__new__(model_class)
            obj.__init__(**json_dict)
            return obj
        else:
            return RallyTypeGeneric(**json_dict)

    def query(self, query: str,
              rally_type: str = None,
              custom_url: str = None,
              fetch: str = "true",
              pagesize: int = 200,
              order_by: str = None,
              workspace: str = None,
              project: str = None,
              model_class: Type[T] = None,
              threads: int = 1) -> List[Union[RallyTypeGeneric, T]]:
        """Generic query over a rally model defined by 'rally_type'

        Ex:
        user: List[User] = query(query="( disabled = true )", rally_type="user", model_class=User)

        Returns: List of RallyTypeGeneric if there is no specific model class, otherwise specific class for
        the model will be returned.
        """
        ws = workspace if workspace else self._workspace
        params = dict(self._baseparams, **{
            "fetch": fetch,
            "pagesize": pagesize,
            "query": query,
            "workspace": ws
        })
        if order_by:
            params["order"] = order_by
        if project:
            params["project"] = project

        if threads > 1:
            return self.get_elements_multithread(params=params, rally_type=rally_type, model_class=model_class,
                                                 thread_number=threads)
        else:
            return self.get_elements(params=params, rally_type=rally_type, model_class=model_class)

    def get_element_by_ref(self, element_ref: str, fetch: str = None,
                           model_class: Type[T] = None) -> Union[RallyTypeGeneric, T]:
        params = self._baseparams
        if fetch:
            params = dict(self._baseparams, fetch=fetch)
        result = self._get(element_ref, params, model_class=model_class)
        return result

    def get_elements_by_ref(self, elements_ref: str, fetch: str = "true", pagesize: int = 500,
                            model_class: Type[T] = None) -> List[Union[RallyTypeGeneric, T]]:
        """
        Returns elements for a list ref as : '<base_url>/project/11111111/artifacts'
        """
        params = dict(self._baseparams, fetch=fetch, pagesize=pagesize)
        results = self._get(url=elements_ref, params=params, model_class=model_class)
        return results

    @requests_error_handling
    def get_elements_total(self, params: dict, rally_type: str) -> int:
        cparams = dict(params, pagesize=1)
        url: str = self._baseurl + rally_type + BaseAPI._security_key
        logger.debug(url)
        response = self._rally_session.get(url, params=cparams)
        rally_raise_errors(response)
        total_res = int(response.json()["QueryResult"]["TotalResultCount"])
        return total_res

    def get_elements(self, params: dict, rally_type: str,
                     keys: List[str] = None, model_class: Type[T] = None) -> List[Union[RallyTypeGeneric, T]]:
        """query and pagesize is included in params"""
        cparams = dict(self._baseparams, **params)
        if model_class:
            rally_types: List[model_class] = []
        else:
            rally_types: List[RallyTypeGeneric] = []

        logger.debug(f"Rally '{rally_type}' query: {cparams['query']}")
        logger.debug(f"Rally '{rally_type}' fetch keys: {keys}")

        page_size: int = int(str(cparams.get("pagesize"))) if cparams.get("pagesize") else 100
        if str(cparams.get("fetch")).lower() != "true" and keys:
            cparams["fetch"] = ",".join(keys)

        total_result_count = self.get_elements_total(cparams, rally_type)
        # Reset page_size
        cparams["pagesize"] = page_size
        iters = math.ceil(total_result_count / page_size)
        start_index: int = 1
        # Main pagination loop
        for i in tqdm.tqdm(range(iters), desc=f"Query pagesize: {page_size} - iterations"):
            rally_types.extend(self._simple_query(cparams, rally_type, keys, model_class=model_class))
            logger.debug(f"Got '{rally_type}' elements from Total: {total_result_count}")
            logger.debug(f"page size: {page_size}, start index: {start_index}")
            start_index = start_index + page_size
            cparams["start"] = start_index

        logger.debug(f"'{rally_type}' query total result: {len(rally_types)}")
        return rally_types

    def get_elements_multithread(self, params: dict, rally_type: str,
                                 model_class: Type[T] = RallyTypeGeneric, thread_number: int = 4,
                                 header_keys: List[str] = None) -> List[T]:
        ## query and pagesize is included in params
        cparams = dict(self._baseparams, **params)
        logger.debug(f"Rally '{rally_type}' query: {cparams['query']}")
        logger.debug(f"Rally '{rally_type}' fetch keys: {header_keys}")
        page_size: int = int(str(cparams.get("pagesize"))) if cparams.get("pagesize") else 100
        if str(cparams.get("fetch")).lower() != "true" and header_keys:
            cparams["fetch"] = ",".join(header_keys)

        total_result_count = self.get_elements_total(cparams, rally_type)
        # Reset page_size
        params["pagesize"] = page_size
        iters = math.ceil(total_result_count / page_size)
        start_index: int = 1
        futures_lst: list = list()
        with FuturesSession(max_workers=thread_number, session=self._rally_session) as fsession:

            # Main pagination loop
            for i in range(iters):
                iheaders = copy.deepcopy(self._rally_session.headers)
                iheaders["start"] = str(start_index)
                iparams = copy.deepcopy(cparams)
                iparams["start"] = str(start_index)
                url = self._baseurl + rally_type
                futures_lst.append(fsession.get(url, params=iparams, headers=iheaders))
                start_index += page_size

            results_index: Dict[int, List] = {}
            for future in tqdm.tqdm(futures.as_completed(futures_lst), desc="Reiciving results", total=iters):
                response: Response = future.result()
                rally_raise_errors(response)
                results = response.json()["QueryResult"]["Results"]
                rally_types: List[model_class] = []
                for result in results:
                    trimed_res = {key: result[key] for key in header_keys} if header_keys else result
                    rally_types.append(self._get_rally_object(trimed_res, model_class=model_class))
                total_res = int(response.json()["QueryResult"]["TotalResultCount"])
                start_index = int(response.request.headers["start"])
                message = (f"Got {len(rally_types)} '{rally_type}' elements from Total: {total_res}, "
                           f"page size: {page_size}, start index: {start_index}")
                logger.debug(message)
                results_index[start_index] = rally_types
        ## Order results using start index of every page.
        ordered_keys: List[int] = sorted(results_index.keys())
        rally_types_total: List[model_class] = []
        for key in ordered_keys:
            rally_types_total.extend(results_index[key])
        logger.debug(f"'{rally_type}' query total result: {len(rally_types_total)}")
        return rally_types_total
