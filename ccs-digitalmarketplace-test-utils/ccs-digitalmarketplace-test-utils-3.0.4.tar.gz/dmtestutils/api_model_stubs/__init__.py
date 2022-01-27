from .base import BaseAPIModelStub
from .audit_event import AuditEventStub
from .brief import BriefStub
from .brief_response import BriefResponseStub
from .framework import FrameworkStub
from .framework_agreement import FrameworkAgreementStub
from .lot import LotStub, as_a_service_lots, cloud_lots, dos_lots
from .services import ArchivedServiceStub, DraftServiceStub, ServiceStub
from .supplier import SupplierStub
from .supplier_framework import SupplierFrameworkStub


# TODO: Flesh out the stubs below and move to their own modules


class DirectAwardProjectStub(BaseAPIModelStub):
    resource_name = 'project'
    default_data = {

    }


class DirectAwardSearchStub(BaseAPIModelStub):
    resource_name = 'search'
    default_data = {

    }


class OutcomeStub(BaseAPIModelStub):
    resource_name = 'outcome'
    default_data = {

    }


class UserStub(BaseAPIModelStub):
    resource_name = 'users'
    default_data = {

    }
