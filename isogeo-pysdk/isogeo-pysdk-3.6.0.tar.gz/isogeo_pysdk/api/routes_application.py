# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Applications entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Application, Workgroup
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
class ApiApplication:
    """Routes as methods of Isogeo API used to manipulate applications."""

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
        super(ApiApplication, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(
        self,
        workgroup_id: str = None,
        include: tuple = ("_abilities",),
        caching: bool = 1,
    ) -> list:
        """Get all applications which are accessible by the authenticated user OR applications for a
        workgroup.

        :param str workgroup_id: identifier of the owner workgroup. If `None`, then list applications for the autenticated user
        :param tuple include: additionnal subresource to include in the response.
        :param bool caching: option to cache the response
        """
        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL
        if workgroup_id is not None:
            logger.debug(
                "Listing applications for a workgroup: {}".format(workgroup_id)
            )
            if not checker.check_is_uuid(workgroup_id):
                raise ValueError(
                    "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
                )
            else:
                url_applications = utils.get_request_base_url(
                    route="groups/{}/applications".format(workgroup_id)
                )
        else:
            logger.debug(
                "Listing applications for the authenticated user: {}".format(
                    self.api_client._user.contact.name
                )
            )
            url_applications = utils.get_request_base_url(route="applications")

        # request
        req_applications = self.api_client.get(
            url=url_applications,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_applications)
        if isinstance(req_check, tuple):
            return req_check

        applications = req_applications.json()

        # if caching use or store the workgroup applications
        if caching and workgroup_id is None:
            self.api_client._applications_names = {
                i.get("name"): i.get("_id") for i in applications
            }
        elif caching:
            self.api_client._wg_applications_names = {
                i.get("name"): i.get("_id") for i in applications
            }
        else:
            pass

        # end of method
        return applications

    @ApiDecorators._check_bearer_validity
    def get(
        self, application_id: str, include: tuple = ("_abilities", "groups")
    ) -> Application:
        """Get details about a specific application.

        :param str application_id: application UUID
        :param tuple include: additionnal subresource to include in the response
        """
        # check application UUID
        if not checker.check_is_uuid(application_id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application_id)
            )
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL
        url_application = utils.get_request_base_url(
            route="applications/{}".format(application_id)
        )

        # request
        req_application = self.api_client.get(
            url=url_application,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Application(**req_application.json())

    @ApiDecorators._check_bearer_validity
    def create(self, application: Application, check_exists: int = 1) -> Application:
        """Add a new application to Isogeo.

        :param int check_exists: check if a application already exists inot the workgroup:

        - 0 = no check
        - 1 = compare name [DEFAULT]

        :param class application: Application model object to create
        """
        # check if application already exists in workgroup
        if check_exists == 1:
            # retrieve workgroup applications
            if not self.api_client._applications_names:
                self.listing(include=())
            # check
            if application.name in self.api_client._applications_names:
                logger.debug(
                    "Application with the same name already exists: {}. Use 'application_update' instead.".format(
                        application.name
                    )
                )
                return False
        else:
            pass

        # URL
        url_application_create = utils.get_request_base_url(route="applications")

        # request
        req_new_application = self.api_client.post(
            url=url_application_create,
            json=application.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_application)
        if isinstance(req_check, tuple):
            return req_check

        # load new application and save it to the cache
        new_application = Application(**req_new_application.json())
        self.api_client._applications_names[new_application.name] = new_application._id

        # end of method
        return new_application

    @ApiDecorators._check_bearer_validity
    def delete(self, application_id: str):
        """Delete a application from Isogeo database.

        :param str application_id: identifier of the resource to delete
        """
        # check application UUID
        if not checker.check_is_uuid(application_id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application_id)
            )
        else:
            pass

        # request URL
        url_application_delete = utils.get_request_base_url(
            route="applications/{}".format(application_id)
        )

        # request
        req_application_deletion = self.api_client.delete(
            url=url_application_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_application_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, application_id: str) -> bool:
        """Check if the specified application exists and is available for the authenticated user.

        :param str application_id: identifier of the application to verify
        """
        # check application UUID
        if not checker.check_is_uuid(application_id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application_id)
            )
        else:
            pass

        # URL builder
        url_application_exists = "{}{}".format(
            utils.get_request_base_url("applications"), application_id
        )

        # request
        req_application_exists = self.api_client.get(
            url_application_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_application_exists

    @ApiDecorators._check_bearer_validity
    def update(self, application: Application, caching: bool = 1) -> Application:
        """Update a application owned by a workgroup.

        :param class application: Application model object to update
        :param bool caching: option to cache the response
        """
        # check application UUID
        if not checker.check_is_uuid(application._id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application._id)
            )
        else:
            pass

        # URL
        url_application_update = utils.get_request_base_url(
            route="applications/{}".format(application._id)
        )

        # request
        req_application_update = self.api_client.put(
            url=url_application_update,
            json=application.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application_update)
        if isinstance(req_check, tuple):
            return req_check

        # update application in cache
        new_application = Application(**req_application_update.json())
        if caching:
            self.api_client._applications_names[
                new_application.name
            ] = new_application._id

        # end of method
        return new_application

    # -- Routes to manage the related objects ------------------------------------------
    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def workgroups(self, application_id: str = None) -> list:
        """Get all groups associated with an application.

        :param str application_id: identifier of the application
        """
        # check application UUID
        if not checker.check_is_uuid(application_id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application_id)
            )
        else:
            pass

        # handling request parameters
        # if isinstance(include, (tuple, list)):
        #     payload = {"_include": ",".join(include)}
        # else:
        #     payload = None

        # URL
        url_application_groups = utils.get_request_base_url(
            route="applications/{}/groups".format(application_id)
        )

        # request
        req_applications = self.api_client.get(
            url=url_application_groups,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_applications)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_applications.json()

    @ApiDecorators._check_bearer_validity
    def associate_group(
        self, application: Application, workgroup: Workgroup, force: bool = 0
    ) -> tuple:
        """Associate a application with a workgroup.

        :param Application application: Application model object to update
        :param Workgroup workgroup: object to associate
        :param bool force: option to force association with multiple groups changing the `canHaveManyGroups` property
        """
        # check application UUID
        if not checker.check_is_uuid(application._id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application._id)
            )
        else:
            pass

        # check workgroup UUID
        if not checker.check_is_uuid(workgroup._id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup._id)
            )
        else:
            pass

        # check application type
        if application.type != "group":
            raise TypeError(
                "Association between applications and workgroup is only possible for 'group applications' type not '{}'".format(
                    application.type
                )
            )
        else:
            pass

        # ensure that application got its groups included. If not, then make a new request to get it.
        """
            For dev memory, there are two main cases:

            Case 1 - application with no groups associated yet:
            - self.get(application_id=app_uuid, include=()).groups[0] is None
            - len(self.get(application_id=app_uuid, include=()).groups) == 1

            Case 2 - application with some groups already associated but without include:
            - self.get(application_id=app_uuid, include=()).groups[0] is None
            - len(self.get(application_id=app_uuid, include=()).groups) == 1
        """
        if len(application.groups) and application.groups[0] is None:
            logger.debug(
                "Application doesn't contain its included workgroups. Let's make a new request..."
            )
            application = self.get(application_id=application._id, include=("groups",))
        else:
            pass

        # check if the application can get multiple groups
        if not application.canHaveManyGroups and len(application.groups) >= 1:
            logger.debug(
                "Application can be associated with only one group and has already one."
            )
            if force:
                logger.debug(
                    "Force mode enabled: application is being updated to be associated to multiple groups."
                )
                application.canHaveManyGroups = True
                self.update(application)
            elif not force:
                logger.error(
                    "Force mode disabled: application can't be associated to multiple groups. Update the application or use force mode."
                )
                return (0, "Application can't be associated to multiple groups.")
        else:
            pass

        # URL
        url_application_association = utils.get_request_base_url(
            route="applications/{}/groups/{}".format(application._id, workgroup._id)
        )

        # request
        req_application_assocation = self.api_client.put(
            url=url_application_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application_assocation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_application_assocation

    @ApiDecorators._check_bearer_validity
    def dissociate_group(self, application: Application, workgroup: Workgroup) -> tuple:
        """Removes the association between the specified group and the specified application.

        :param Application application: Application model object to update
        :param Workgroup workgroup: object to associate
        """
        # check application UUID
        if not checker.check_is_uuid(application._id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application._id)
            )
        else:
            pass

        # check workgroup UUID
        if not checker.check_is_uuid(workgroup._id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup._id)
            )
        else:
            pass

        # check application type
        if application.type != "group":
            raise TypeError(
                "Association between applications and workgroup is only possible for 'group applications' type not '{}'".format(
                    application.type
                )
            )
        else:
            pass

        # URL
        url_application_dissociation = utils.get_request_base_url(
            route="applications/{}/groups/{}".format(application._id, workgroup._id)
        )

        # request
        req_application_dissociation = self.api_client.delete(
            url=url_application_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_application_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_application_dissociation


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_application = ApiApplication()
