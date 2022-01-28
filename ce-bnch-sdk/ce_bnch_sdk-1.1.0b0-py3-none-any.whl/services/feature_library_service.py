from typing import Iterable, List, Optional

from benchling_api_client.api.feature_libraries import list_feature_libraries
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import FeatureLibrariesPaginatedList, FeatureLibrary, ListFeatureLibrariesSort
from benchling_sdk.services.base_service import BaseService


class FeatureLibraryService(BaseService):
    """
    Feature Libraries.

    Feature Libraries are collections of shared canonical patterns that can be used to generate annotations
    on matching regions of DNA Sequences or AA Sequences.

    See https://benchling.com/api/reference#/Feature%20Libraries
    """

    @api_method
    def _feature_libraries_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        sort: Optional[ListFeatureLibrariesSort] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[FeatureLibrariesPaginatedList]:

        return list_feature_libraries.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ids=none_as_unset(optional_array_query_param(ids)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            sort=none_as_unset(sort),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        sort: Optional[ListFeatureLibrariesSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[FeatureLibrary]:
        """
        List Feature Libraries.

        See https://benchling.com/api/reference#/Feature%20Libraries/listFeatureLibraries
        """

        def api_call(next_token: NextToken) -> Response[FeatureLibrariesPaginatedList]:
            return self._feature_libraries_page(
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ids=ids,
                names_any_of=names_any_of,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: FeatureLibrariesPaginatedList) -> Optional[List[FeatureLibrary]]:
            return body.feature_libraries

        return PageIterator(api_call, results_extractor)
