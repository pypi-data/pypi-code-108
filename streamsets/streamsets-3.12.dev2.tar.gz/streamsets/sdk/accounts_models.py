# Copyright 2020 StreamSets Inc.

import collections
import dpath
import logging
import requests

from .models import BaseModel, ModelCollection
from .utils import (MutableKwargs, SeekableList)

logger = logging.getLogger(__name__)

dpath.options.ALLOW_EMPTY_STRING_KEYS = True

ModelCollectionResults = collections.namedtuple('ModelCollectionResults', ['results', 'kwargs'])


class Release(BaseModel):
    """Model for a release e.g. a transformer, SDC.

    Attributes:
        date (:obj:`int`):
        distributionGroups (:obj:`list`):
        documentationLink (:obj:`str`):
        extras (:obj:`dist`):
        featured (:obj:`bool`):
        label (:obj:`str`):
        product (:obj:`str`):
        releaseNotesLink (:obj:`str`):
        version (:obj:`str`):
    """
    _ATTRIBUTES_TO_IGNORE = []
    _ATTRIBUTES_TO_REMAP = {'distribution_groups': 'distributionGroups',
                            'documentation_link': 'documentationLink',
                            'release_notes_link': 'releaseNotesLink'}
    _REPR_METADATA = ['product', 'version']

    def __init__(self, release):
        super().__init__(release,
                         attributes_to_ignore=Release._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Release._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Release._REPR_METADATA)


class Releases(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.account_models.Release` instances.

    Args:
        accounts (:py:class:`streamsets.sdk.accounts.Accounts`): Accounts object.
    """

    def __init__(self, accounts):
        self._accounts = accounts
        self._id_attr = 'distribution_key'

    def _get_all_results_from_api(self, **kwargs):
        """

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.accounts_models.Release` instances and
        """
        kwargs_instance = MutableKwargs({}, kwargs)
        try:
            result = SeekableList(Release(release)
                                  for release in
                                  self._accounts.
                                  api_client.return_all_releases().response.json()['data']['releases'])
        except requests.exceptions.HTTPError:
            raise ValueError('No releases found')
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)
