# Copyright 2016 VMware, Inc.
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
#

from oslo_utils import excutils

from vmware_nsxlib._i18n import _


class NsxLibException(Exception):
    """Base NsxLib Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred.")

    def __init__(self, **kwargs):
        try:
            super(NsxLibException, self).__init__(self.message % kwargs)
            self.msg = self.message % kwargs
        except Exception:
            with excutils.save_and_reraise_exception() as ctxt:
                if not self.use_fatal_exceptions():
                    ctxt.reraise = False
                    # at least get the core message out if something happened
                    super(NsxLibException, self).__init__(self.message)

    def __str__(self):
        return self.msg

    def use_fatal_exceptions(self):
        return False


class ObjectAlreadyExists(NsxLibException):
    message = _("%(object_type)s already exists")


class NotImplemented(NsxLibException):
    message = _("%(operation)s is not supported")


class ObjectNotGenerated(NsxLibException):
    message = _("%(object_type)s was not generated")


class CertificateError(NsxLibException):
    message = _("Certificate error: %(msg)s")


class NsxLibInvalidInput(NsxLibException):
    message = _("Invalid input for operation: %(error_message)s.")


class ManagerError(NsxLibException):
    message = _("Unexpected error from backend manager (%(manager)s) "
                "for %(operation)s%(details)s")
    related_error_codes = []
    related_status_codes = []

    def __init__(self, **kwargs):
        details = kwargs.get('details', '')
        kwargs['details'] = ': %s' % details if details else ''
        super(ManagerError, self).__init__(**kwargs)
        try:
            self.msg = self.message % kwargs
        except KeyError:
            self.msg = details
        self.error_code = kwargs.get('error_code')
        self.related_error_codes = kwargs.get('related_error_codes', [])
        self.status_code = kwargs.get('status_code')
        self.related_status_codes = kwargs.get('related_status_codes', [])


class ResourceNotFound(ManagerError):
    message = _("Resource could not be found on backend (%(manager)s) for "
                "%(operation)s")


class MultipleResourcesFound(ManagerError):
    message = _("Multiple resources are found on backend (%(manager)s) for "
                "%(operation)s, where only one is expected")


class BackendResourceNotFound(ResourceNotFound):
    message = _("%(details)s On backend (%(manager)s) with Operation: "
                "%(operation)s")


class InvalidInput(ManagerError):
    message = _("%(operation)s failed: Invalid input %(arg_val)s "
                "for %(arg_name)s")


class RealizationError(ManagerError):
    pass


class RealizationErrorStateError(RealizationError):
    message = _("%(resource_type)s ID %(resource_id)s is in ERROR state: "
                "%(error)s")


class RealizationTimeoutError(RealizationError):
    message = _("%(resource_type)s ID %(resource_id)s "
                "was not realized after %(attempts)s attempts "
                "with %(sleep)s seconds sleep")


class DetailedRealizationTimeoutError(RealizationError):
    message = _("%(resource_type)s ID %(resource_id)s "
                "was not realized to %(realized_type)s "
                "for %(related_type)s %(related_id)s "
                "after %(attempts)s attempts "
                "with %(sleep)s seconds sleep")


class StaleRevision(ManagerError):
    pass


class ServerBusy(ManagerError):
    pass


class TooManyRequests(ServerBusy):
    pass


class ServiceUnavailable(ServerBusy):
    pass


class ClientCertificateNotTrusted(ManagerError):
    message = _("Certificate not trusted")


class BadXSRFToken(ManagerError):
    message = _("Bad or expired XSRF token")


class InvalidCredentials(ManagerError):
    message = _("Failed to authenticate with NSX: %(msg)s")


class InvalidLicense(ManagerError):
    message = _("No valid License to configure NSX resources: %(msg)s")


class BadJSONWebTokenProviderRequest(NsxLibException):
    message = _("Bad or expired JSON web token request from provider: %(msg)s")


class ServiceClusterUnavailable(ManagerError):
    message = _("Service cluster: '%(cluster_id)s' is unavailable. Please, "
                "check NSX setup and/or configuration")


class NSGroupMemberNotFound(ManagerError):
    message = _("Could not find NSGroup %(nsgroup_id)s member %(member_id)s "
                "for removal.")


class NSGroupIsFull(ManagerError):
    message = _("NSGroup %(nsgroup_id)s contains has reached its maximum "
                "capacity, unable to add additional members.")


class SecurityGroupMaximumCapacityReached(ManagerError):
    message = _("Security Group %(sg_id)s has reached its maximum capacity, "
                "no more ports can be associated with this security-group.")


class NsxSearchInvalidQuery(NsxLibException):
    message = _("Invalid input for NSX search query. Reason: %(reason)s")


class NsxSearchError(NsxLibException):
    message = _("Search failed due to error")


class NsxIndexingInProgress(NsxSearchError):
    message = _("Bad Request due to indexing is in progress, please retry "
                "after sometime")


class NsxSearchTimeout(NsxSearchError):
    message = _("Request timed out. This may occur when system is under load "
                "or running low on resources")


class NsxSearchOutOfSync(NsxSearchError):
    message = _("Index is currently out of sync")


class NsxSearchPipelineError(NsxLibException):
    message = _("Exception while searching during pipeline execution")


class NsxPendingDelete(NsxLibException):
    message = _("An object with the same name is marked for deletion. Either "
                "use another path or wait for the purge cycle to permanently "
                "remove the deleted object")


class NsxInvalidPath(ManagerError):
    message = _("Invalid path found: %(details)s")


class NsxSegemntWithVM(ManagerError):
    message = _("Cannot delete segment as it still has VMs or VIFs attached")


class NsxOverlapAddresses(NsxLibInvalidInput):
    message = _("Overlapping addresses found: %(details)s")


class NsxOverlapVlan(NsxLibInvalidInput):
    message = _("Duplicate logical-switch vlan-ids sharing same underlying "
                "physical devices resulting in a conflict")


class APITransactionAborted(ManagerError):
    message = _("API transaction aborted as MP cluster is reconfiguring")


class CannotConnectToServer(ManagerError):
    message = _("Cannot connect to server")


class ResourceInUse(ManagerError):
    message = _("The object cannot be deleted as either it has children or it "
                "is being referenced by other objects")
