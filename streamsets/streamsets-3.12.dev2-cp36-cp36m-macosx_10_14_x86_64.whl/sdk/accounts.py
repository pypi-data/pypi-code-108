# Copyright 2020 StreamSets Inc.

"""Abstractions for interacting with StreamSets Accounts."""

import logging

from . import accounts_api

from .accounts_models import Releases

logger = logging.getLogger(__name__)


class Accounts:
    """Class to interact with StreamSets Accounts.

    Args:
        accounts_server_url (:obj:`str`): StreamSets Accounts server base URL.
        accounts_authentication_token (:obj:`str`): StreamSets Accounts authentication token.
    """
    VERIFY_SSL_CERTIFICATES = True

    def __init__(self,
                 accounts_server_url,
                 accounts_authentication_token):
        self.server_url = accounts_server_url
        self._authentication_token = accounts_authentication_token

        session_attributes = {'verify': self.VERIFY_SSL_CERTIFICATES}
        self.api_client = accounts_api.ApiClient(server_url=self.server_url,
                                                 authentication_token=self._authentication_token,
                                                 session_attributes=session_attributes)

        self.api_client.login()

    def logout(self):
        self.api_client.logout()

    @property
    def _releases(self):
        """Releases.

        Returns:
            An instance of :py:obj:`streamsets.sdk.accounts_models.Releases`.
        """
        return Releases(self)

    def get_download_link(self, product, target_operating_system, download_type, product_version=None):
        """Get the download link for the specified product.

        Args:
            product (:py:obj:`str`): product e.g. transformer, datacollector
            target_operating_system (:py:obj:`str`): target operating system e.g. macos, linux
            download_type (:py:obj:`str`): Distribution's download type
            product_version (:py:obj:`str`): product version e.g. '3.15.0' Default: ``None``

        Returns:
            An instance of :obj:`str`
        """
        if download_type == 'Docker':
            raise ValueError('Docker downloads need to happen from docker hub')

        # Way to fetch one particular releases for a product and version
        if product_version:
            release = self._releases.get(product=product, version=product_version)
        else:
            # If featured = true, then that is the latest version which is returned here.
            releases = self._releases.get_all(product=product)
            release = [item for item in releases if item.featured][0]

        # Get the distribution key and platforms for the release
        def find_distribution_key():
            for group in release.distribution_groups:
                for distribution in group['distributions']:
                    if distribution['type'] == download_type and target_operating_system in distribution['platforms']:
                        return distribution['distributionKey']

        distribution_key = find_distribution_key()
        if not distribution_key:
            distribution_type_set, platforms_set, product_set = _get_release_data(releases)
            raise Exception(f'Distribution key not found for the product={product}, '
                            f'target_operating_system={target_operating_system} '
                            f'download_type={download_type}, product_version={product_version}'
                            f'\n Valid download_types are: {distribution_type_set}'
                            f' \n and valid target_operating_systems are: {platforms_set}'
                            f' \n and valid products are: {product_set}')

        # Fetch the details for this release
        data = self.api_client.get_distribution(distribution_key=distribution_key,
                                                platform=target_operating_system).response.json()['data']
        return data['distLink']


def _get_release_data(releases):
    distribution_type_set = set()
    platforms_set = set()
    product_set = set()
    for release in releases:
        product_set.add(release.product)
        for group in release.distribution_groups:
            for distribution in group['distributions']:
                # print(distribution['type'])
                distribution_type_set.add(distribution['type'])
                platforms_set.update(distribution['platforms'])
    return sorted(distribution_type_set), sorted(platforms_set), sorted(product_set)
