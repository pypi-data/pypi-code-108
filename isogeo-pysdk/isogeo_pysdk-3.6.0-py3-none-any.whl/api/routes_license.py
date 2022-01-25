# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Licenses (= CGUs, conditions) entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# 3rd party
from requests.models import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Condition, License, Metadata
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
class ApiLicense:
    """Routes as methods of Isogeo API used to manipulate licenses (conditions)."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

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
        super(ApiLicense, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(
        self,
        workgroup_id: str = None,
        include: tuple = ("_abilities", "count"),
        caching: bool = 1,
    ) -> list:
        """Get workgroup licenses.

        :param str workgroup_id: identifier of the owner workgroup
        :param tuple include: additionnal subresource to include in the response
        :param bool caching: option to cache the response
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # request URL
        url_licenses = utils.get_request_base_url(
            route="groups/{}/licenses".format(workgroup_id)
        )

        # request
        req_wg_licenses = self.api_client.get(
            url_licenses,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_wg_licenses)
        if isinstance(req_check, tuple):
            return req_check

        wg_licenses = req_wg_licenses.json()

        # if caching use or store the workgroup licenses
        if caching and not self.api_client._wg_licenses_names:
            self.api_client._wg_licenses_names = {
                i.get("name"): i.get("_id") for i in wg_licenses
            }

        # end of method
        return wg_licenses

    @ApiDecorators._check_bearer_validity
    def get(self, license_id: str) -> License:
        """Get details about a specific license.

        :param str license_id: license UUID
        """
        # check license UUID
        if not checker.check_is_uuid(license_id):
            raise ValueError("License ID is not a correct UUID.")
        else:
            pass

        # license route
        url_license = utils.get_request_base_url(route="licenses/{}".format(license_id))

        # request
        req_license = self.api_client.get(
            url=url_license,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_license)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return License(**req_license.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, check_exists: int = 1, license: object = License()
    ) -> License:
        """Add a new license to a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param int check_exists: check if a license already exists inot the workgroup:

        - 0 = no check
        - 1 = compare name [DEFAULT]

        :param class license: License model object to create
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # check if license already exists in workgroup
        if check_exists == 1:
            # retrieve workgroup licenses
            if not self.api_client._wg_licenses_names:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if license.name in self.api_client._wg_licenses_names:
                logger.debug(
                    "License with the same name already exists: {}. Use 'license_update' instead.".format(
                        license.name
                    )
                )
                return False
        else:
            pass

        # build request url
        url_license_create = utils.get_request_base_url(
            route="groups/{}/licenses".format(workgroup_id)
        )

        # request
        req_new_license = self.api_client.post(
            url_license_create,
            data=license.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_license)
        if isinstance(req_check, tuple):
            return req_check

        # load new license and save it to the cache
        new_license = License(**req_new_license.json())
        self.api_client._wg_licenses_names[new_license.name] = new_license._id

        # end of method
        return new_license

    @ApiDecorators._check_bearer_validity
    def delete(self, workgroup_id: str, license_id: str):
        """Delete a license from Isogeo database.

        :param str workgroup_id: identifier of the owner workgroup
        :param str license_id: identifier of the resource to delete
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check license UUID
        if not checker.check_is_uuid(license_id):
            raise ValueError("License ID is not a correct UUID: {}".format(license_id))
        else:
            pass

        # request URL
        url_license_delete = utils.get_request_base_url(
            route="groups/{}/licenses/{}".format(workgroup_id, license_id)
        )

        # request
        req_license_deletion = self.api_client.delete(
            url_license_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_license_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_license_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, license_id: str) -> bool:
        """Check if the specified license exists and is available for the authenticated user.

        :param str license_id: identifier of the license to verify
        """
        # check license UUID
        if not checker.check_is_uuid(license_id):
            raise ValueError("License ID is not a correct UUID: {}".format(license_id))
        else:
            pass

        # URL builder
        url_license_exists = "{}{}".format(
            utils.get_request_base_url("licenses"), license_id
        )

        # request
        req_license_exists = self.api_client.get(
            url_license_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_license_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_license_exists

    @ApiDecorators._check_bearer_validity
    def update(self, license: License, caching: bool = 1) -> License:
        """Update a license owned by a workgroup.

        :param class license: License model object to update
        :param bool caching: option to cache the response
        """
        # check license UUID
        if not checker.check_is_uuid(license._id):
            raise ValueError("License ID is not a correct UUID: {}".format(license._id))
        else:
            pass

        # URL
        url_license_update = utils.get_request_base_url(
            route="groups/{}/licenses/{}".format(license.owner.get("_id"), license._id)
        )

        # request
        req_license_update = self.api_client.put(
            url=url_license_update,
            data=license.to_dict(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_license_update)
        if isinstance(req_check, tuple):
            return req_check

        # update license in cache
        new_license = License(**req_license_update.json())
        if caching:
            self.api_client._wg_licenses_names[new_license.name] = new_license._id

        # end of method
        return new_license

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def associate_metadata(
        self, metadata: Metadata, license: License, description: str, force: bool = 0
    ) -> Response:
        """Associate a condition (license + specific description) to a metadata. When a license is
        associated to a metadata, it becomes a condition.

        By default, if the specified license is already associated, the method won't duplicate the association.
        Use `force` option to overpass this behavior.

        :param Metadata metadata: metadata object to update
        :param License license: license model object to associate
        :param str description: additional description to add to the association. Optional.
        :param bool force: force association even if the same license is already associated

        :Example:

        >>> # retrieve objects to be associated
        >>> md = isogeo.metadata.get(
                metadata_id="6b5cc93626634d0e9b0d2c48eff96bc3",
                include=['conditions']
            )
        >>> lic = isogeo.license.license("f6e0c665905a4feab1e9c1d6359a225f")
        >>> # associate them
        >>> isogeo.license.associate_metadata(
                metadata=md,
                license=lic,
                description="Specific description for this license when applied to this metadata."
            )
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check license UUID
        if not checker.check_is_uuid(license._id):
            raise ValueError("License ID is not a correct UUID: {}".format(license._id))
        else:
            pass

        # check if the license is already associated
        if not force:
            if metadata.conditions:
                # conditions have been included during request and contains conditions
                logger.debug(
                    "Conditions have been included during request and contains conditions. Lets' check if the asked license is already associated or not."
                )
                # list licenses uuids
                if license._id in [
                    condition.get("license").get("_id")
                    for condition in metadata.conditions
                ]:
                    logger.info(
                        "License ({} - {}) is already associated to this metadata ({} - {}).".format(
                            license._id, license.name, metadata._id, metadata.name
                        )
                        + " If you still want to add a duplicate license, use the `force` option."
                    )
                    return False, 409
            elif hasattr(metadata, "conditions") and metadata.conditions == []:
                logger.debug(
                    "Conditions have been included during request but are empty."
                )
            elif metadata.conditions is None:
                logger.info(
                    "Conditions have not been included during request. So, let's renew it!"
                )
                metadata_with_conditions = self.api_client.metadata.get(
                    metadata_id=metadata._id, include=("conditions",)
                )
                return self.associate_metadata(
                    metadata=metadata_with_conditions,
                    license=license,
                    description=description,
                    force=force,
                )
            else:
                pass
        else:
            logger.warning(
                "Force option enabled. Ignoring existing associated licenses. Risk of duplicated association."
            )

        # pass it to the conditions route
        condition_to_create = Condition(description=description, license=license)

        # end of method
        return self.api_client.metadata.conditions.create(
            metadata=metadata, condition=condition_to_create
        )


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_license = ApiLicense()
