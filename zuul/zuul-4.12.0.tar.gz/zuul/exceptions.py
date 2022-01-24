# Copyright 2015 Rackspace Australia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


class ChangeNotFound(Exception):
    def __init__(self, number, ps):
        self.number = number
        self.ps = ps
        self.change = "%s,%s" % (str(number), str(ps))
        message = "Change %s not found" % self.change
        super(ChangeNotFound, self).__init__(message)


class RevNotFound(Exception):
    def __init__(self, project, rev):
        self.project = project
        self.revision = rev
        message = ("Failed to checkout project '%s' at revision '%s'"
                   % (self.project, self.revision))
        super(RevNotFound, self).__init__(message)


class MergeFailure(Exception):
    pass


class ConfigurationError(Exception):
    pass


class StreamingError(Exception):
    pass


# Authentication Exceptions

class AuthTokenException(Exception):
    defaultMsg = 'Unknown Error'
    HTTPError = 400

    def __init__(self, realm=None, msg=None):
        super(AuthTokenException, self).__init__(msg or self.defaultMsg)
        self.realm = realm
        self.error = self.__class__.__name__
        self.error_description = msg or self.defaultMsg

    def getAdditionalHeaders(self):
        return {}


class JWKSException(AuthTokenException):
    defaultMsg = 'Unknown error involving JSON Web Key Set'


class AuthTokenForbiddenException(AuthTokenException):
    defaultMsg = 'Insufficient privileges'
    HTTPError = 403


class AuthTokenUnauthorizedException(AuthTokenException):
    defaultMsg = 'This action requires authentication'
    HTTPError = 401

    def getAdditionalHeaders(self):
        error_header = '''Bearer realm="%s"
       error="%s"
       error_description="%s"'''
        return {"WWW-Authenticate": error_header % (self.realm,
                                                    self.error,
                                                    self.error_description)}


class AuthTokenUndecodedException(AuthTokenUnauthorizedException):
    default_msg = 'Auth Token could not be decoded'


class AuthTokenInvalidSignatureException(AuthTokenUnauthorizedException):
    default_msg = 'Invalid signature'


class BearerTokenRequiredError(AuthTokenUnauthorizedException):
    defaultMsg = 'Authorization with bearer token required'


class IssuerUnknownError(AuthTokenUnauthorizedException):
    defaultMsg = 'Issuer unknown'


class MissingClaimError(AuthTokenUnauthorizedException):
    defaultMsg = 'Token is missing claims'


class IncorrectAudienceError(AuthTokenUnauthorizedException):
    defaultMsg = 'Incorrect audience'


class TokenExpiredError(AuthTokenUnauthorizedException):
    defaultMsg = 'Token has expired'


class MissingUIDClaimError(MissingClaimError):
    defaultMsg = 'Token is missing id claim'


class IncorrectZuulAdminClaimError(AuthTokenUnauthorizedException):
    defaultMsg = (
        'The "zuul.admin" claim is expected to be a list of tenants')


class UnauthorizedZuulAdminClaimError(AuthTokenUnauthorizedException):
    defaultMsg = 'Issuer is not allowed to set "zuul.admin" claim'
