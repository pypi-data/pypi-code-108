# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Search

    See: http://help.isogeo.com/api/complete/index.html#definition-resource
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from functools import lru_cache, partial

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import MetadataSearch
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiSearch:
    """Routes as methods of Isogeo API used to manipulate metadatas (resources)."""

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

        # ensure platform to request
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
        super(ApiSearch, self).__init__()

    # -- Routes to search --------------------------------------------------------------
    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def search(
        self,
        # application or group
        group: str = None,
        # semantic and objects filters
        query: str = "",
        share: str = None,
        specific_md: tuple = (),
        # results model
        include: tuple = (),
        # geographic filters
        bbox: tuple = None,
        poly: str = None,
        georel: str = None,
        # sorting
        order_by: str = "_created",
        order_dir: str = "desc",
        # results size
        page_size: int = 20,
        offset: int = 0,
        # specific options of implemention
        augment: bool = False,
        check: bool = True,
        expected_total: int = None,
        tags_as_dicts: bool = False,
        whole_results: bool = False,
    ) -> MetadataSearch:
        """Search within the resources shared to the application. It's the mainly used method to
        retrieve metadata.

        :param str group: context to search. Pass a workgroup UUID to search within a \
            group or pass None (default) to search in a global context.
        :param str query: search terms and semantic filters. Equivalent of
         **q** parameter in Isogeo API. It could be a simple
         string like *oil* or a tag like *keyword:isogeo:formations*
         or *keyword:inspire-theme:landcover*. The *AND* operator
         is applied when various tags are passed.
        :param tuple bbox: Bounding box to limit the search. Must be a 4 tuple of \
            coordinates in WGS84 (EPSG 4326). Could be associated with *georel*.
        :param str poly: Geographic criteria for the search, in WKT format. \
            Could be associated with *georel*.
        :param str georel: geometric operator to apply to the `bbox` or `poly` parameters. \
            Available values:

            * 'contains',
            * 'disjoint',
            * 'equals',
            * 'intersects' - [APPLIED BY API if NOT SPECIFIED]
            * 'overlaps',
            * 'within'.

        :param str order_by: sorting results. Available values:

            * '_created': metadata creation date [DEFAULT if relevance is null]
            * '_modified': metadata last update
            * 'title': metadata title
            * 'created': data creation date (possibly None)
            * 'modified': data last update date
            * 'relevance': relevance score calculated by API [DEFAULT].

        :param str order_dir: sorting direction. Available values:

            * 'desc': descending
            * 'asc': ascending

        :param int page_size: limits the number of results.
         Useful to paginate results display. Default value: 100.
        :param int offset: offset to start page size
         from a specific results index
        :param str share: share UUID to filter on
        :param tuple specific_md: list of metadata UUIDs to filter on
        :param tuple include: subresources that should be returned. See: :py:class:`enums.MetadataSubresources`.
        :param bool whole_results: option to return all results or only the page size. *False* by DEFAULT.
        :param bool check: option to check query parameters and avoid erros. *True* by DEFAULT.
        :param bool augment: option to improve API response by adding some tags on the fly (like shares_id)
        :param int expected_total: if different of None, value will be used to paginate. Can save a request.
        :param bool tags_as_dicts: option to store tags as key/values by filter.

        :rtype: MetadataSearch

        :Example:

        .. code-block:: python

            # get the search context (without results), useful to populate a search widget
            search_context = isogeo.search(page_size=0, whole_results=0, augment=1)

            # search the 10 first results in alphabetically order
            search_10 = isogeo.search(
                page_size=10,
                include="all",
                order_by="title",
                order_dir="asc",
                expected_total=search_context.total
            )

            # returns all results, filtering on vector-datasets
            search_full = isogeo.search(
                query="type:vector-dataset",
                order_by="title",
                order_dir="desc",
                include="all",
                augment=1,
                whole_results=1
            )
        """
        # handling request parameters
        payload = {
            "_id": checker._check_filter_specific_md(specific_md),
            "_include": checker._check_filter_includes(
                includes=include, entity="metadata"
            ),
            "_limit": page_size,
            "_offset": offset,
            "box": bbox,
            "geo": poly,
            "rel": georel,
            "ob": order_by,
            "od": order_dir,
            "q": query,
            "s": share,
        }

        # check query parameters
        if query and check:
            checker.check_request_parameters(payload)
        else:
            pass

        # URL
        if group is None:
            logger.debug("Searching as application")
            url_resources_search = utils.get_request_base_url(route="resources/search")
        elif checker.check_is_uuid(group):
            logger.debug("Searching as group")
            url_resources_search = utils.get_request_base_url(
                route="groups/{}/resources/search".format(group)
            )
        else:
            raise ValueError

        # SEARCH CASES

        # CASE - MULTIPLE PAGINATED SEARCHES
        if whole_results:
            # PAGINATION
            # determine if a request to get the total is required
            if expected_total is None:
                # make an empty request with same filters
                total_results = self.search(
                    # search context: application or group
                    group=group,
                    # filters
                    query=query,
                    share=share,
                    specific_md=specific_md,
                    bbox=bbox,
                    georel=georel,
                    poly=poly,
                    # options
                    augment=0,
                    check=0,
                    page_size=0,
                    whole_results=0,
                ).total
            else:
                total_results = expected_total

            # avoid to launch async searches if it's possible in one request
            if total_results <= 100:
                logger.debug(
                    "Paginated (size={}) search changed into a unique search because "
                    "the total of metadata {} is less than the maximum size (100).".format(
                        page_size, total_results
                    )
                )
                return self.search(
                    # search context: application or group
                    group=group,
                    # filters
                    query=query,
                    share=share,
                    specific_md=specific_md,
                    bbox=bbox,
                    georel=georel,
                    poly=poly,
                    # results
                    include=include,
                    # sorting
                    order_by=order_by,
                    order_dir=order_dir,
                    # options
                    augment=augment,
                    check=0,
                    page_size=100,
                    whole_results=0,
                )
            else:
                # store search args as dict
                search_params = {
                    # search context: application or group
                    "group": group,
                    # filters
                    "query": query,
                    "include": include,
                    "share": share,
                    "specific_md": specific_md,
                    "bbox": bbox,
                    "georel": georel,
                    "poly": poly,
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
                    self.search_metadata_asynchronous(
                        total_results=total_results, **search_params
                    ),
                    loop=self.loop,
                )
                self.loop.run_until_complete(future_searches_concatenated)

                # check results structure
                req_metadata_search = future_searches_concatenated.result()

                # properly close the loop
                self.loop.close()

        # cASE - NO PAGINATION NEEDED
        elif page_size == 0 or not whole_results:
            logger.debug(
                "Simple search with page parameters offset={} - page_size={}".format(
                    offset, page_size
                )
            )

            # request
            req_metadata_search = self.api_client.get(
                url=url_resources_search,
                headers=self.api_client.header,
                params=payload,
                proxies=self.api_client.proxies,
                verify=self.api_client.ssl,
                timeout=(5, 200),
            )

            # checking response
            req_check = checker.check_api_response(req_metadata_search)
            if isinstance(req_check, tuple):
                return req_check

            req_metadata_search = MetadataSearch(**req_metadata_search.json())

        # add shares to tags and query
        if augment:
            self.add_tags_shares(req_metadata_search)
            if share:
                req_metadata_search.query["_shares"] = [share]
            else:
                req_metadata_search.query["_shares"] = []
        else:
            pass

        # store tags in dicts
        if tags_as_dicts:
            new_tags = utils.tags_to_dict(
                tags=req_metadata_search.tags, prev_query=req_metadata_search.query
            )
            # clear
            req_metadata_search.tags.clear()
            req_metadata_search.query.clear()
            # update
            req_metadata_search.tags.update(new_tags[0])
            req_metadata_search.query.update(new_tags[1])
        else:
            pass

        # end of method
        return req_metadata_search

    # -- SEARCH SUBMETHODS
    async def search_metadata_asynchronous(
        self, total_results: int, max_workers: int = 10, **kwargs
    ) -> MetadataSearch:
        """Meta async method used to request big searches (> 100 results), using asyncio. It's a
        private method launched by the main search method.

        :param int total_results: total of results to retrieve
        :param int max_workers: maximum number of thread to use :class:`python.concurrent.futures`

        :rtype: MetadataSearch
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
                        self.search,
                        # search context: application or group
                        group=kwargs.get("group"),
                        # filters
                        query=kwargs.get("query"),
                        include=kwargs.get("include"),
                        share=kwargs.get("share"),
                        specific_md=kwargs.get("specific_md"),
                        bbox=kwargs.get("bbox"),
                        poly=kwargs.get("poly"),
                        georel=kwargs.get("georel"),
                        # sorting
                        order_by=kwargs.get("order_by"),
                        order_dir=kwargs.get("order_dir"),
                        # pagination
                        offset=offset,
                        page_size=100,
                        # options
                        augment=0,
                        check=0,
                        expected_total=total_results,
                        tags_as_dicts=0,
                        whole_results=0,
                    ),
                )
                for offset in li_offsets
            ]

            # store responses in a fresh Metadata Search object
            final_search = MetadataSearch(results=[], query={}, tags={})
            for response in await asyncio.gather(*tasks):
                final_search.envelope = response.envelope
                final_search.limit = response.total
                final_search.offset = 0
                final_search.query.update(response.query)
                final_search.results.extend(response.results)
                final_search.tags.update(response.tags)
                final_search.total = response.total

            return final_search

    # -- UTILITIES -----------------------------------------------------------
    def add_tags_shares(self, search: MetadataSearch):
        """Add shares list to the tags attributes in search.

        :param MetadataSearch search: search to add shares
        """
        # check if shares_id have already been retrieved or not
        if not hasattr(self.api_client, "shares_id"):
            shares = self.api_client.share.listing()
            self.api_client.shares_id = {
                "share:{}".format(i.get("_id")): i.get("name") for i in shares
            }
        else:
            pass
        # update query tags
        search.tags.update(self.api_client.shares_id)


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    api_search = ApiSearch()
    print(api_search)
