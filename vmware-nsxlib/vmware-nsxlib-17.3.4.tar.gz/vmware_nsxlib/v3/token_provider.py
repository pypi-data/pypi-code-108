# Copyright 2019 VMware, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc


# NOTE: Consider inheriting from an abstract TokenProvider class to share
#       interface with XSRF token
class AbstractJWTProvider(object, metaclass=abc.ABCMeta):
    """Interface for providers of JSON Web Tokens(JWT)

    Responsible to provide the token value and refresh it once expired,
    or on demand, for authorization of requests to NSX.
    """

    @abc.abstractmethod
    def get_token(self, refresh_token=False):
        """Request JWT value.

        :param refresh_token: Boolean value, indicating whether a new token
                              value is to be retrieved.
        :raises vmware_nsxlib.v3.exceptions.BadJSONWebTokenProviderRequest:
        """
        pass

    def get_header_value(self, token_value):
        return "Bearer %s" % token_value
