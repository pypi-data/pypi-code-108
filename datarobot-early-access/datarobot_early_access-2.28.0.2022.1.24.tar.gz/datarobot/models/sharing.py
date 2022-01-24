#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import String
from datarobot.models.api_object import APIObject

from ..utils import encode_utf8_if_py2


class SharingAccess(APIObject):
    """ Represents metadata about whom a entity (e.g. a data store) has been shared with

    .. versionadded:: v2.14

    Currently :py:class:`DataStores <datarobot.DataStore>`,
    :py:class:`DataSources <datarobot.DataSource>`,
    :py:class:`Projects <datarobot.models.Project>` (new in version v2.15) and
    :py:class:`CalendarFiles <datarobot.CalendarFile>` (new in version 2.15) can be shared.

    This class can represent either access that has already been granted, or be used to grant access
    to additional users.

    Attributes
    ----------
    username : str
        a particular user
    role : str or None
        if a string, represents a particular level of access and should be one of
        ``datarobot.enums.SHARING_ROLE``.  For more information on the specific access levels, see
        the :ref:`sharing <sharing>` documentation.  If None, can be passed to a `share`
        function to revoke access for a specific user.
    can_share : bool or None
        if a bool, indicates whether this user is permitted to further share.  When False, the
        user has access to the entity, but can only revoke their own access but not modify any
        user's access role.  When True, the user can share with any other user at a access role up
        to their own.  May be None if the SharingAccess was not retrieved from the DataRobot server
        but intended to be passed into a `share` function; this will be equivalent to passing True.
    user_id : str
        the id of the user
    """

    _converter = t.Dict(
        {
            t.Key("username"): String,
            t.Key("role"): String,
            t.Key("can_share", default=None): t.Or(t.Bool, t.Null),
            t.Key("user_id", default=None): t.Or(String, t.Null),
        }
    ).ignore_extra("*")

    def __init__(self, username, role, can_share=None, user_id=None):
        self.username = username
        self.role = role
        self.can_share = can_share
        self.user_id = user_id

    def __repr__(self):
        return encode_utf8_if_py2(
            (
                "{cls}(username: {username}, role: {role}, "
                "can_share: {can_share}, user_id: {user_id})"
            ).format(
                cls=self.__class__.__name__,
                username=self.username,
                role=self.role,
                can_share=self.can_share,
                user_id=self.user_id,
            )
        )

    def collect_payload(self):
        """ Set up the dict that should be sent to the server in order to share this

        Returns
        -------
        payload : dict
        """
        payload = {"username": self.username, "role": self.role}
        if self.can_share is not None:
            payload["can_share"] = self.can_share
        return payload
