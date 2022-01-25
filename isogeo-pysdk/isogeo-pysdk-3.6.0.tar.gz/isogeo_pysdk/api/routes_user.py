# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Users entities

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
from isogeo_pysdk.models import Contact, User
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
class ApiUser:
    """Routes as methods of Isogeo API used to manipulate users."""

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
        super(ApiUser, self).__init__()

    # -- Routes to manage the  User objects ---------------------------------------
    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(self) -> list:
        """Get registered users.

        :Example:

        >>> # get all registered users
        >>> users = isogeo.user.listing()
        >>> print(len(users))
        925
        >>> # filter on staff users (as list)
        >>> staff = [user for user in users if user.get("staff")]
        >>> print(len(staff))
        10
        >>> # filter on users with an email from isogeo(as list)
        >>> users_isogeo = [user for user in users if "@isogeo" in user.get("contact").get("email")]
        >>> print(len(users_isogeo))
        37
        """
        # handling request parameters
        payload = {"_include": "memberships"}

        # request URL
        url_users = utils.get_request_base_url(route="users")

        # request
        req_users = self.api_client.get(
            url=url_users,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_users)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_users.json()

    @ApiDecorators._check_bearer_validity
    def get(self, user_id: str, include: tuple = ("_abilities")) -> User:
        """Get details about a specific user.

        :param str user_id: user UUID
        :param list include: additionnal subresource to include in the response

        :rtype: User
        """
        # check user UUID
        if not checker.check_is_uuid(user_id):
            raise ValueError("User ID is not a correct UUID: {}".format(user_id))
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL
        url_user = utils.get_request_base_url(route="users/{}".format(user_id))

        # request
        req_user = self.api_client.get(
            url=url_user,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_user)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return User(**req_user.json())

    @ApiDecorators._check_bearer_validity
    def create(self, user: object = User, check_exists: bool = 1) -> User:
        """Add a new user to Isogeo.

        :param class user: User model object to create
        :param bool check_exists: check if a user already exists:

        - 0 = no check
        - 1 = compare email [DEFAULT]

        """
        # check if object has a correct contact
        if not hasattr(user, "contact") or not isinstance(user.contact, Contact):
            raise ValueError(
                "`user.contact.name` and `user.contact.email` are required to create a user."
            )

        # check if user with same email already exists
        if check_exists:
            # retrieve users
            existing_users = self.listing()
            # check
            if user.contact.email in [
                uzer.get("contact").get("email") for uzer in existing_users
            ]:
                logger.error(
                    "User with the same email already exists: {}. Use 'user_update' instead.".format(
                        user.contact.email
                    )
                )
                return False
        else:
            pass

        # URL
        url_user_create = utils.get_request_base_url(route="users")

        # request
        req_new_user = self.api_client.post(
            url=url_user_create,
            json=user.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_user)
        if isinstance(req_check, tuple):
            return req_check

        # load new user and save it to the cache
        new_user = User(**req_new_user.json())

        # end of method
        return new_user

    @ApiDecorators._check_bearer_validity
    def delete(self, user: User) -> User:
        """Delete an user.

        :param class user: User model object to be deteled

        :rtype: User
        """
        # check user UUID
        if not checker.check_is_uuid(user._id):
            raise ValueError("User ID is not a correct UUID: {}".format(user._id))
        else:
            pass

        # URL
        url_user_delete = utils.get_request_base_url(route="users/{}".format(user._id))

        # request
        req_user_delete = self.api_client.delete(
            url=url_user_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_user_delete)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_check

    @ApiDecorators._check_bearer_validity
    def update(self, user: User) -> User:
        """Update an user.

        :param class user: User model object to be updated

        :rtype: User

        :Example:

        .. code-block:: python

            # retrieve the user
            uzer = isogeo.user.get(user_id={user_uuid})

            # unsubscribe the user from a newsletter
            uzer.mailchimp.get("subscriptions")[0]["isInterested"] = False

            # update it online
            isogeo.user.update(uzer)
        """
        # check user UUID
        if not checker.check_is_uuid(user._id):
            raise ValueError("User ID is not a correct UUID: {}".format(user._id))
        else:
            pass

        # URL
        url_user_update = utils.get_request_base_url(route="users/{}".format(user._id))

        # request
        req_user_update = self.api_client.put(
            url=url_user_update,
            json=user.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_user_update)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return User(**req_user_update.json())

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def memberships(self, user_id: str) -> dict:
        """Returns memberships for the specified user.

        :param str user_id: user UUID
        """
        logger.warning(
            "This route doesn't work in 2019. See: https://github.com/isogeo/isogeo-api/issues/7"
        )
        # URL builder
        url_user_memberships = utils.get_request_base_url(
            route="users/{}/memberships".format(user_id)
        )

        # request
        req_user_memberships = self.api_client.get(
            url=url_user_memberships,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_user_memberships)
        if isinstance(req_check, tuple):
            return req_check

        return req_user_memberships.json()

    @ApiDecorators._check_bearer_validity
    def subscriptions(self, user: User, subscription: str, subscribe: bool) -> User:
        """Subscribe or unsubscribe an user to/from one of the available subscriptions.

        :param class user: User model object to be updated
        :param str subscription: subscription (newsletter) targetted. Must be one of: NewReleases | TipsAndTricks
        :param bool subscribe: subscribe (1) or unsubscribe (0)

        :rtype: User

        :Example:

        .. code-block:: python

            # retrieve the user
            uzer = isogeo.user.get(user_id={user_uuid})

            # unsubscribe the user from the newsletter 'TipsAndTricks'
            isogeo.user.subscriptions(uzer, "TipsAndTricks", 0)

            # subscribe the user to the newsletter 'NewReleases'
            isogeo.user.subscriptions(uzer, "TipsAndTricks", 0)
        """
        # check user UUID
        if not checker.check_is_uuid(user._id):
            raise ValueError("User ID is not a correct UUID: {}".format(user._id))
        else:
            pass

        # check subscription
        if subscription not in ("NewReleases", "TipsAndTricks"):
            raise ValueError(
                "Subscription '{}' is not one of accepted values: {}".format(
                    subscription, " | ".join(["NewReleases", "TipsAndTricks"])
                )
            )

        # retrieve the existing subscription
        user_subscription = [
            newsletter
            for newsletter in user.mailchimp.get("subscriptions")
            if newsletter.get("name") == subscription
        ][0]

        # compare subscription status with required update
        if user_subscription.get("isInterested") == subscribe:
            logger.debug(
                "Subscription '{}' has already the required value: {}".format(
                    subscription, subscribe
                )
            )
            return user
        else:
            user_subscription["isInterested"] = bool(subscribe)

        # URL
        url_user_update = utils.get_request_base_url(route="users/{}".format(user._id))

        # request
        req_user_update = self.api_client.put(
            url=url_user_update,
            json=user.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_user_update)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return User(**req_user_update.json())


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_user = ApiUser()
