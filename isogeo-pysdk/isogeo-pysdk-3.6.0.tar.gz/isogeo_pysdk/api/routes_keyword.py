#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Keywords entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from functools import partial

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Keyword, KeywordSearch, Metadata, Workgroup
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Global #############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiKeyword:
    """Routes as methods of Isogeo API used to manipulate keywords."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # create an asyncio AbstractEventLoop
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError as e:
            logger.warning(
                "Async get loop failed. Maybe because it's already executed in a separated thread. Original error: {}".format(
                    e
                )
            )
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # store API client (Request [Oauthlib] Session) and pass it to the decorators
        self.api_client = api_client
        ApiDecorators.api_client = api_client

        # ensure platform and others params to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(self.api_client.platform)
        # initialize
        super(ApiKeyword, self).__init__()

    @ApiDecorators._check_bearer_validity
    def metadata(
        self,
        metadata_id: str = None,
        include: tuple = ("_abilities", "count", "thesaurus"),
    ) -> list:
        """List a metadata's keywords with complete information.

        :param str metadata_id: metadata UUID
        :param tuple include: subresources that should be returned. Available values:

          * '_abilities'
          * 'count'
          * 'thesaurus'

        :rtype: list
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL
        url_metadata_keywords = utils.get_request_base_url(
            route="resources/{}/keywords/".format(metadata_id)
        )

        # request
        req_metadata_keywords = self.api_client.get(
            url=url_metadata_keywords,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_keywords)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_metadata_keywords.json()

    @ApiDecorators._check_bearer_validity
    def thesaurus(
        self,
        thesaurus_id: str = "1616597fbc4348c8b11ef9d59cf594c8",
        query: str = "",
        offset: int = 0,
        order_by: str = "text",  # available values : count.group, count.isogeo, text
        order_dir: str = "desc",
        page_size: int = 100,
        specific_md: list = [],
        specific_tag: list = [],
        include: tuple = ("_abilities", "count"),
        whole_results: bool = True,
    ) -> KeywordSearch:
        """Search for keywords within a specific thesaurus or a specific group.

        :param str thesaurus_id: thesaurus UUID
        :param str query: search terms, equivalent of **q** parameter in API.
        :param int offset: offset to start page size from a specific results index
        :param str order_by: sorting results. Available values:

          * 'count.isogeo': count of associated resources within Isogeo
          * 'text': alphabetical order  [DEFAULT if relevance is null]

        :param str order_dir: sorting direction. Available values:

          * 'desc': descending [DEFAULT]
          * 'asc': ascending

        :param int page_size: limits the number of results. Default: 100.
        :param list specific_md: list of metadata UUIDs to filter on
        :param list specific_tag: list of tags UUIDs to filter on
        :param tuple include: subresources that should be returned. Available values:

          * '_abilities'
          * 'count'
          * 'thesaurus'

        :param bool whole_results: option to return all results or only the page size. *False* by DEFAULT.

        :rtype: KeywordSearch
        """

        # handling request parameters
        payload = {
            "_id": checker._check_filter_specific_md(specific_md),
            "_include": checker._check_filter_includes(include, "keyword"),
            "_limit": page_size,
            "_offset": offset,
            "_tag": checker._check_filter_specific_tag(specific_tag),
            "ob": order_by,
            "od": order_dir,
            "q": query,
        }

        # URL
        url_thesauri_keywords = utils.get_request_base_url(
            route="thesauri/{}/keywords/search".format(thesaurus_id)
        )

        if whole_results:
            # PAGINATION
            # determine if a request to get the total is required
            # make an empty request with same filters
            total_results = self.thesaurus(
                thesaurus_id=thesaurus_id,
                # filters
                query=query,
                specific_md=specific_md,
                specific_tag=specific_tag,
                # options
                page_size=1,
                whole_results=0,
            ).total

            # avoid to launch async searches if it's possible in one request
            if total_results <= 100:
                logger.debug(
                    "Paginated (size={}) search changed into a unique search because "
                    "the total of metadata {} is less than the maximum size (100).".format(
                        page_size, total_results
                    )
                )
                return self.thesaurus(
                    thesaurus_id=thesaurus_id,
                    # filters
                    query=query,
                    specific_md=specific_md,
                    specific_tag=specific_tag,
                    # results
                    include=include,
                    # sorting
                    order_by=order_by,
                    order_dir=order_dir,
                    # options
                    page_size=100,
                    whole_results=0,
                )
            else:
                # store search args as dict
                search_params = {
                    "thesaurus_id": thesaurus_id,
                    # filters
                    "query": query,
                    "include": include,
                    "specific_md": specific_md,
                    "specific_tag": specific_tag,
                    # sorting
                    "order_by": order_by,
                    "order_dir": order_dir,
                }

                # check loop state
                if self.loop.is_closed():
                    logger.debug(
                        "Current event loop is already closed. Creating a new one..."
                    )
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)

                # launch async searches
                future_searches_concatenated = asyncio.ensure_future(
                    self.search_keyword_asynchronous(
                        total_results=total_results, **search_params
                    ),
                    loop=self.loop,
                )
                self.loop.run_until_complete(future_searches_concatenated)

                # check results structure
                req_keyword_search = future_searches_concatenated.result()

                # properly close the loop
                self.loop.close()
        else:
            # request
            req_thesaurus_keywords = self.api_client.get(
                url=url_thesauri_keywords,
                headers=self.api_client.header,
                params=payload,
                proxies=self.api_client.proxies,
                verify=self.api_client.ssl,
                timeout=self.api_client.timeout,
            )

            # checking response
            req_check = checker.check_api_response(req_thesaurus_keywords)
            if isinstance(req_check, tuple):
                return req_check

            req_keyword_search = KeywordSearch(**req_thesaurus_keywords.json())

        # end of method
        return req_keyword_search

    @ApiDecorators._check_bearer_validity
    def workgroup(
        self,
        workgroup_id: str = None,
        thesaurus_id: str = None,
        query: str = "",
        offset: int = 0,
        order_by: str = "text",  # available values : count.group, count.isogeo, text
        order_dir: str = "desc",
        page_size: int = 100,
        specific_md: list = [],
        specific_tag: list = [],
        include: tuple = ("_abilities", "count", "thesaurus"),
        whole_results: bool = True,
    ) -> KeywordSearch:
        """Search for keywords within a specific group's used thesauri.

        :param str thesaurus_id: thesaurus UUID to filter on
        :param str query: search terms, equivalent of **q** parameter in API.
        :param int offset: offset to start page size from a specific results index
        :param str order_by: sorting results. Available values:

          * 'count.group': count of associated resources within the specified group
          * 'count.isogeo': count of associated resources within Isogeo
          * 'text': alphabetical order  [DEFAULT]

        :param str order_dir: sorting direction. Available values:

          * 'desc': descending [DEFAULT]
          * 'asc': ascending

        :param int page_size: limits the number of results. Default: 100.
        :param list specific_md: list of metadata UUIDs to filter on
        :param list specific_tag: list of tags UUIDs to filter on
        :param tuple include: subresources that should be returned. Available values:

          * '_abilities'
          * 'count'
          * 'thesaurus'

        :param bool whole_results: option to return all results or only the page size. *False* by DEFAULT.
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        payload = {
            "_id": checker._check_filter_specific_md(specific_md),
            "_include": checker._check_filter_includes(include, "keyword"),
            "_limit": page_size,
            "_offset": offset,
            "_tag": checker._check_filter_specific_tag(specific_tag),
            "th": thesaurus_id,
            "ob": order_by,
            "od": order_dir,
            "q": query,
        }

        if whole_results:
            # PAGINATION
            # determine if a request to get the total is required
            # make an empty request with same filters
            total_results = self.workgroup(
                workgroup_id=workgroup_id,
                thesaurus_id=thesaurus_id,
                # filters
                query=query,
                specific_md=specific_md,
                specific_tag=specific_tag,
                # options
                page_size=1,
                whole_results=False,
            ).total

            # avoid to launch async searches if it's possible in one request
            if total_results > page_size:
                payload["_limit"] = total_results
            else:
                pass
        else:
            pass

        # URL
        url_workgroup_keywords = utils.get_request_base_url(
            route="groups/{}/keywords/search".format(workgroup_id)
        )

        # request
        req_workgroup_keywords = self.api_client.get(
            url=url_workgroup_keywords,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_workgroup_keywords)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return KeywordSearch(**req_workgroup_keywords.json())

    @ApiDecorators._check_bearer_validity
    def get(
        self, keyword_id: str, include: tuple = ("_abilities", "count", "thesaurus")
    ) -> Keyword:
        """Get details about a specific keyword.

        :param str keyword_id: keyword UUID
        :param tuple include: additionnal subresource to include in the response


        :Example:

        >>> # get a metadata with its tags (or keywords)
        >>> md = isogeo.metadata.get(METADATA_UUID, include=("tags",))
        >>> # list Isogeo keywords
        >>> li_keywords_uuids = [
            tag[8:] for tag in self.metadata_source.tags
            if tag.startswith("keyword:isogeo:")
            ]
        >>> # pick a random one
        >>> random_keyword = sample(li_keywords_uuid, 1)[0]
        >>> # get its details
        >>> keyword = isogeo.keyword.get(random_keyword)
        """
        # request parameter
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # keyword route
        url_keyword = utils.get_request_base_url(route="keywords/{}".format(keyword_id))

        # request
        req_keyword = self.api_client.get(
            url=url_keyword,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Keyword(**req_keyword.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self,
        keyword: Keyword,
        thesaurus_id: str = "1616597fbc4348c8b11ef9d59cf594c8",
        check_exists: bool = 0,
    ) -> Keyword:
        """Add a new keyword to the Isogeo thesaurus.

        If a keyword with the same text already exists, the Isogeo API returns a 409 HTTP code.
        Then this method will try to get the closest matching keyword and return it.

        :param Keyword keyword: Keyword model object to create
        :param str thesaurus_id: thesaurus UUID
        :param bool check_exists: check if a keyword with the same text already exists. Defaults to False.
        """
        # check if thesaurus is 'group-theme' or 'isogeo'
        if thesaurus_id not in [
            "1616597fbc4348c8b11ef9d59cf594c8",
            "0edc90b138ef41e593cf47fbca2cb1ad",
        ]:
            raise ValueError(
                "'thesaurus_id' value can only be '1616597fbc4348c8b11ef9d59cf594c8' or '0edc90b138ef41e593cf47fbca2cb1ad', not '{}'".format(
                    thesaurus_id
                )
            )
        else:
            pass

        if check_exists:
            # search for thesaurus' keywords
            thesaurus_existing_keywords = self.thesaurus(
                thesaurus_id=thesaurus_id,
                query=keyword.text,
                include=(),
                whole_results=True,
            )
            if (
                thesaurus_existing_keywords.results
                and len(thesaurus_existing_keywords.results) > 0
            ):
                # search for a perfectly matching keyword
                li_matching_keyword = [
                    Keyword(**kw)
                    for kw in thesaurus_existing_keywords.results
                    if kw.get("text") == keyword.text
                ]
                # return it if it exists
                if len(li_matching_keyword) > 0:
                    return li_matching_keyword[0]
                else:
                    pass
            else:
                pass
        else:
            pass

        # URL
        url_keyword_create = utils.get_request_base_url(
            route="thesauri/{}/keywords".format(thesaurus_id)
        )

        # request
        req_new_keyword = self.api_client.post(
            url=url_keyword_create,
            json=keyword.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_new_keyword)
        if isinstance(req_check, tuple):
            # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
            if req_check[1] == 409:
                # search for thesaurus' keywords
                thesaurus_existing_keywords = self.thesaurus(
                    thesaurus_id=thesaurus_id,
                    query=keyword.text,
                    include=(),
                    whole_results=True,
                )
                if (
                    thesaurus_existing_keywords.results
                    and len(thesaurus_existing_keywords.results) > 0
                ):
                    # search for a perfectly matching keyword
                    li_matching_keyword = [
                        Keyword(**kw)
                        for kw in thesaurus_existing_keywords.results
                        if kw.get("text") == keyword.text
                    ]
                    # return it if it exists
                    if len(li_matching_keyword) > 0:
                        return li_matching_keyword[0]
                    else:
                        pass
                else:
                    pass
            # if other error, then return it
            return req_check
        else:
            # end of method
            return Keyword(**req_new_keyword.json())

    @ApiDecorators._check_bearer_validity
    def delete(
        self, keyword: Keyword, thesaurus_id: str = "1616597fbc4348c8b11ef9d59cf594c8"
    ) -> Keyword:
        """Delete a keyword from Isogeo database.

        :param Keyword keyword: Keyword model object to create
        :param str thesaurus_id: thesaurus UUID
        """
        # check keyword UUID
        if not checker.check_is_uuid(keyword._id):
            raise ValueError("Keyword ID is not a correct UUID: {}".format(keyword._id))
        else:
            pass
        # check if thesaurus is 'group-theme' or 'isogeo'
        if thesaurus_id not in [
            "1616597fbc4348c8b11ef9d59cf594c8",
            "0edc90b138ef41e593cf47fbca2cb1ad",
        ]:
            raise ValueError(
                "'thesaurus_id' value can only be '1616597fbc4348c8b11ef9d59cf594c8' or '0edc90b138ef41e593cf47fbca2cb1ad', not '{}'".format(
                    thesaurus_id
                )
            )
        else:
            pass

        # URL
        url_keyword_delete = utils.get_request_base_url(
            route="thesauri/{}/keywords/{}".format(thesaurus_id, keyword._id)
        )

        # request
        req_keyword_deletion = self.api_client.delete(
            url=url_keyword_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_keyword_deletion

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def tagging(
        self, metadata: Metadata, keyword: Keyword, check_exists: bool = 0
    ) -> dict:
        """Associate a keyword to a metadata.

        :param Metadata metadata: metadata (resource) to edit
        :param Keyword keyword: object to associate
        :param bool check_exists: check if the keyword is already tagged to the metadata. Defaults to False.

        :Example:

        .. code-block:: python

            # retrieve a metadata
            md = isogeo.metadata.get(METADATA_UUID)
            # retrieve a keyword
            kw = isogeo.keyword.get(KEYWORD_UUID)
            # associate a keyword to a metadata
            isogeo.keyword.tagging(metadata = md, keyword = kw)
        """
        # check contact UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check keyword UUID
        if not checker.check_is_uuid(keyword._id):
            raise ValueError("Keyword ID is not a correct UUID: {}".format(keyword._id))
        else:
            pass

        # check if kyword is already associated
        if check_exists:
            # retrieve metadata existing keywords
            if metadata.tags:
                # first look into the tags
                metadata_existing_keywords = [
                    tag
                    for tag in metadata.tags
                    if tag.startswith("keyword:isogeo:")
                    or tag.startswith("keyword:group-theme:")
                ]
            elif metadata.keywords:
                # if not, maybe the metadata has been passed with subresuorces: so use it
                metadata_existing_keywords = [
                    tag
                    for tag in metadata.keywords
                    if tag.get("_tag").startswith("keyword:isogeo:")
                    or tag.get("_tag").startswith("keyword:group-theme:")
                ]
            else:
                # if not, make a new request to perform the check
                metadata_existing_keywords = self.metadata(
                    metadata_id=metadata._id, include=()
                )

                metadata_existing_keywords = [
                    tag
                    for tag in metadata_existing_keywords
                    if tag.get("_tag").startswith("keyword:isogeo:")
                    or tag.get("_tag").startswith("keyword:group-theme:")
                ]
            # then compare
            if keyword._tag in metadata_existing_keywords:
                logger.info(
                    "Keyword {} is already associated with the metadata {}. Tagging operation cancelled.".format(
                        keyword._tag, metadata._id
                    )
                )
                # return checker as true
                return True, 204

        else:
            pass

        # URL
        url_keyword_associate = utils.get_request_base_url(
            route="resources/{}/keywords/{}".format(metadata._id, keyword._id)
        )

        # request
        req_keyword_associate = self.api_client.post(
            url=url_keyword_associate,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword_associate)
        if isinstance(req_check, tuple):
            # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
            if req_check[1] == 409:
                # log conflict
                logger.info(
                    "Metadata '{}' is already tagged by the keyword '{}'. Isogeo API reply: HTTP {} - {}.".format(
                        metadata._id,
                        keyword._id,
                        req_check[1],
                        req_keyword_associate.reason,
                    )
                )
                # set checker as true
                req_check = tuple([True, req_check[1]])
            else:
                return req_check

        # end of method
        return req_keyword_associate

    @ApiDecorators._check_bearer_validity
    def untagging(self, metadata: Metadata, keyword: Keyword) -> dict:
        """Dissociate a keyword from a metadata.

        :param Metadata metadata: metadata (resource) to edit
        :param Keyword keyword: object to associate
        """
        # check contact UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError("Metadata ID is not a correct UUID.")
        else:
            pass

        # check keyword UUID
        if not checker.check_is_uuid(keyword._id):
            raise ValueError("Keyword ID is not a correct UUID.")
        else:
            pass

        # URL
        url_keyword_dissociate = utils.get_request_base_url(
            route="resources/{}/keywords/{}".format(metadata._id, keyword._id)
        )

        # request
        req_keyword_dissociate = self.api_client.delete(
            url=url_keyword_dissociate,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword_dissociate)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_keyword_dissociate

    @ApiDecorators._check_bearer_validity
    def associate_workgroup(
        self, workgroup: Workgroup, keyword: Keyword, check_exists: bool = 1
    ) -> dict:
        """Associate a keyword to a workgroup.

        :param Workgroup workgroup: workgroup (resource) to edit
        :param Keyword keyword: object to associate
        :param bool check_exists: check if the keyword is already associated with the workgroup. Defaults to True.

        :Example:

        .. code-block:: python

            # retrieve a workgroup
            wg = isogeo.workgroup.get(WORKGROUP_UUID)
            # retrieve a keyword
            kw = isogeo.keyword.get(KEYWORD_UUID)
            # associate a keyword to a workgroup
            isogeo.keyword.associate_workgroup(workgroup = wg, keyword = kw)
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup._id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup._id)
            )
        else:
            pass

        # check keyword UUID
        if not checker.check_is_uuid(keyword._id):
            raise ValueError("Keyword ID is not a correct UUID: {}".format(keyword._id))
        else:
            pass

        # check if keyword is from group-theme or isogeo thesaurus
        if "isogeo" not in keyword._tag and "group-theme" not in keyword._tag:
            keyword_thesaurus_code = keyword._tag.replace("keyword:", "").split(":")[0]
            raise ValueError(
                "Keyword can only be from 'isogeo' or 'group-theme' thesaurus, not from '{}' one".format(
                    keyword_thesaurus_code
                )
            )
        # if keyword is form isogeo thesaurus, check if it need to be associated
        elif "isogeo" in keyword._tag and workgroup.areKeywordsRestricted is False:
            # return checker as true
            return True, "not necessary"
        else:
            pass

        # check if keyword is already associated
        if check_exists:
            # search for all workgroup's keywords
            workgroup_existing_keywords = self.workgroup(
                workgroup_id=workgroup._id, whole_results=True
            ).results
            # fetch all workgroup's keywords' tags
            workgroup_existing_keywords = [
                kw.get("_tag")
                for kw in workgroup_existing_keywords
                if kw.get("_tag").startswith("keyword:isogeo:")
                or kw.get("_tag").startswith("keyword:group-theme:")
            ]

            # then compare
            if keyword._tag in workgroup_existing_keywords:
                # return checker as true
                return True, "already done"
            else:
                pass
        else:
            pass

        # URL
        url_keyword_associate_with_workgroup = utils.get_request_base_url(
            route="groups/{}/keywords/{}".format(workgroup._id, keyword._id)
        )

        # request
        req_keyword_associate = self.api_client.post(
            url=url_keyword_associate_with_workgroup,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword_associate)
        if isinstance(req_check, tuple):
            # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
            if req_check[1] == 409:
                # log conflict
                logger.info(
                    "Keyword '{}' is already associated to the workgroup '{}'. Isogeo API reply: HTTP {} - {}.".format(
                        keyword._id,
                        workgroup._id,
                        req_check[1],
                        req_keyword_associate.reason,
                    )
                )
                # set checker as true
                return True, req_check[1]
            else:
                return req_check

        # end of method
        return req_keyword_associate

    @ApiDecorators._check_bearer_validity
    def dissociate_workgroup(
        self, workgroup: Workgroup, keyword: Keyword, check_exists: bool = 1
    ) -> dict:
        """Dissociate a keyword from a workgroup.

        :param Workgroup workgroup: workgroup (resource) to edit
        :param Keyword keyword: object to dissociate
        :param bool check_exists: check if the keyword is already dissociated with the workgroup. Defaults to True.

        :Example:

        .. code-block:: python

            # retrieve a workgroup
            wg = isogeo.workgroup.get(WORKGROUP_UUID)
            # retrieve a keyword
            kw = isogeo.keyword.get(KEYWORD_UUID)
            # dissociate a keyword to a workgroup
            isogeo.keyword.dissociate_workgroup(workgroup = wg, keyword = kw)
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup._id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup._id)
            )
        else:
            pass

        # check keyword UUID
        if not checker.check_is_uuid(keyword._id):
            raise ValueError("Keyword ID is not a correct UUID: {}".format(keyword._id))
        else:
            pass

        # check if keyword is from group-theme or isogeo thesaurus
        if "isogeo" not in keyword._tag and "group-theme" not in keyword._tag:
            keyword_thesaurus_code = keyword._tag.replace("keyword:", "").split(":")[0]
            raise ValueError(
                "Keyword can only be from 'isogeo' or 'group-theme' thesaurus, not from '{}' one".format(
                    keyword_thesaurus_code
                )
            )
        # if keyword is form isogeo thesaurus, check if it need to be dissociated
        elif "isogeo" in keyword._tag and workgroup.areKeywordsRestricted is False:
            # return checker as true
            return True, "not necessary"
        else:
            pass

        # check if keyword is already dissociated
        if check_exists:
            # search for all workgroup's keywords
            workgroup_existing_keywords = self.workgroup(
                workgroup_id=workgroup._id, whole_results=True
            ).results
            # fetch all workgroup's keywords' tags
            workgroup_existing_keywords = [
                kw.get("_tag")
                for kw in workgroup_existing_keywords
                if kw.get("_tag").startswith("keyword:isogeo:")
                or kw.get("_tag").startswith("keyword:group-theme:")
            ]

            # then compare
            if keyword._tag not in workgroup_existing_keywords:
                # return checker as true
                return True, "already done"
        else:
            pass

        # URL
        url_keyword_dissociate_with_workgroup = utils.get_request_base_url(
            route="groups/{}/keywords/{}".format(workgroup._id, keyword._id)
        )

        # request
        req_keyword_dissociate = self.api_client.delete(
            url=url_keyword_dissociate_with_workgroup,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            timeout=self.api_client.timeout,
            verify=self.api_client.ssl,
        )

        # checking response
        req_check = checker.check_api_response(req_keyword_dissociate)
        if isinstance(req_check, tuple):
            # handle conflict (see: https://developer.mozilla.org/fr/docs/Web/HTTP/Status/409)
            if req_check[1] == 404:
                # log conflict
                logger.info(
                    "Keyword '{}' is already dissociated from the workgroup '{}'. Isogeo API reply: HTTP {} - {}.".format(
                        keyword._id,
                        workgroup._id,
                        req_check[1],
                        req_keyword_dissociate.reason,
                    )
                )
                # set checker as true
                return True, req_check[1]
            else:
                return req_check

        # end of method
        return req_keyword_dissociate

    # -- SEARCH SUBMETHODS
    async def search_keyword_asynchronous(
        self, total_results: int, max_workers: int = 10, **kwargs
    ) -> KeywordSearch:
        """Meta async method used to request big searches (> 100 results), using asyncio. It's a
        private method launched by the main search method.

        :param int total_results: total of results to retrieve
        :param int max_workers: maximum number of thread to use :class:`python.concurrent.futures`

        :rtype: KeywordSearch
        """
        # prepare async searches
        total_pages = utils.pages_counter(total_results, page_size=100)
        li_offsets = [offset * 100 for offset in range(0, total_pages)]
        logger.debug("Async search launched with {} pages.".format(total_pages))

        with ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="IsogeoSearch"
        ) as executor:
            self.loop = asyncio.get_event_loop()
            tasks = [
                self.loop.run_in_executor(
                    executor,
                    partial(
                        self.thesaurus,
                        # filters
                        query=kwargs.get("query"),
                        include=kwargs.get("include"),
                        specific_md=kwargs.get("specific_md"),
                        specific_tag=kwargs.get("specific_tag"),
                        # sorting
                        order_by=kwargs.get("order_by"),
                        order_dir=kwargs.get("order_dir"),
                        # pagination
                        offset=offset,
                        page_size=100,
                        # options
                        whole_results=0,
                    ),
                )
                for offset in li_offsets
            ]

            # store responses in a fresh Metadata Search object
            final_search = KeywordSearch(results=[])
            for response in await asyncio.gather(*tasks):
                final_search.limit = response.total
                final_search.offset = 0
                final_search.results.extend(response.results)
                final_search.total = response.total

            return final_search


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_keyword = ApiKeyword()
