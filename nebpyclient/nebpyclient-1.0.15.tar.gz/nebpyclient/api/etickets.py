#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from datetime import datetime
from .graphqlclient import GraphQLParam, NebMixin
from .common import PageInput, NebEnum, ResourceType, read_value
from .sorting import SortDirection


class SupportCaseStatus(NebEnum):
    """Indicates the status of the support case"""

    New = "New"
    Pending = "Pending"
    Working = "Working"
    Escalated = "Escalated"
    Closed = "Closed"


class SupportCaseIssueType(NebEnum):
    """Indicates the type of support case"""

    Question = "Question"
    Hardware = "Hardware"
    Software = "Software"
    FeatureRequest = "FeatureRequest"
    Unknown = "Unknown"


class SupportCasePriority(NebEnum):
    """Indicates the customer specified priority for the support case"""

    High = "High"
    Medium = "Medium"
    Low = "Low"


class SupportCaseSort:
    """A sort object for support cases

    Allows sorting support cases on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            status: SortDirection = None,
            issue_type: SortDirection = None,
            created_date: SortDirection = None,
            updated_date: SortDirection = None
    ):
        """Constructs a new sort object for support cases.

        Allows sorting support cases on common properties. The sort object
        allows only one property to be specified.

        :param status: Sort direction for the ``status`` property of a support
            case object.
        :type status: SortDirection, optional
        :param issue_type: Sort direction for the ``issue_type`` property of a
            support case object.
        :type issue_type: SortDirection, optional
        :param created_date: Sort direction for the ``created_date`` property
            of a support case object.
        :type created_date: SortDirection, optional
        :param updated_date: Sort direction for the ``updated_date`` property of
            a support case object.
        :type updated_date: SortDirection, optional
        """

        self.__status = status
        self.__issue_type = issue_type
        self.__created_date = created_date
        self.__updated_date = updated_date

    @property
    def status(self) -> SortDirection:
        """Sort direction for the ``status`` property of a support case"""
        return self.__status

    @property
    def issue_type(self) -> SortDirection:
        """Sort direction for the ``issue_type`` property of a support case"""
        return self.__issue_type

    @property
    def created_date(self) -> SortDirection:
        """Sort direction for the ``created_date`` property of a support case"""
        return self.__created_date

    @property
    def updated_date(self) -> SortDirection:
        """Sort direction for the ``updated_date`` property of a support case"""
        return self.__updated_date

    @property
    def as_dict(self):
        result = dict()
        result["status"] = self.status
        result["issueType"] = self.issue_type
        result["createdDate"] = self.created_date
        result["updatedDate"] = self.updated_date
        return result


class SupportCaseFilter:
    """A filter object to filter support cases.

    Allows filtering for specific support cases in nebulon ON. The
    filter allows only one property to be specified.
    """

    def __init__(
            self,
            number: str = None,
            status: SupportCaseStatus = None,
            issue_type: SupportCaseIssueType = None,
            contact_uuid: str = None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If defined, one
        parameter must be supplied.

        :param number: Filter based on support case number
        :type number: str, optional
        :param status: Filter based on support case status
        :type status: SupportCaseStatus, optional
        :param issue_type: Filter based on support case type
        :type issue_type: SupportCaseIssueType, optional
        :param contact_uuid: Filter based on the support case contact
        :type contact_uuid: str, optional
        """

        self.__number = number
        self.__status = status
        self.__issue_type = issue_type
        self.__contact_uuid = contact_uuid

    @property
    def number(self) -> str:
        """Filter based on the support case number"""
        return self.__number

    @property
    def status(self) -> SupportCaseStatus:
        """Filter based on the support case status"""
        return self.__status

    @property
    def issue_type(self) -> SupportCaseIssueType:
        """Filter based on the support case type"""
        return self.__issue_type

    @property
    def contact_uuid(self) -> str:
        """Filter based on the support case contact"""
        return self.__contact_uuid

    @property
    def as_dict(self):
        result = dict()
        result["number"] = self.number
        result["status"] = self.status
        result["issueType"] = self.issue_type
        result["contactID"] = self.contact_uuid
        return result


class CreateSupportCaseInput:
    """An input object to create a new support case

    Allows creation of a support case in nebulon ON. A support case allows
    customers to get their issues associated with nebulon Cloud-Defined Storage
    to be resolved with their preferred support channel. Issues may include
    infrastructure and hardware issues, software issues, or questions.
    """

    def __init__(
            self,
            subject: str,
            description: str,
            priority: SupportCasePriority,
            issue_type: SupportCaseIssueType,
            spu_serial: str = None,
            resource_type: ResourceType = None,
            resource_id: str = None
    ):
        """Constructs a new input object to create a support case

        Depending on the type of support case the required parameters change.
        At a minimum, customers need to supply a ``subject`` that describes the
        high level summary of the issue, a ``description`` that details their
        specific problem, a ``priority`` to indicate the urgency of the request,
        and the ``issue_type`` to better route the support case to the appropriate
        subject matter expert.

        If the issue is related to a specific services processing unit (SPU) or
        resource in nebulon ON or in the customer's datacenter, ``spu_serial``,
        ``resource_type``, and ``resource_id`` shall be specified.

        :param subject: High level summary of an issue
        :type subject: str
        :param description: Detailed description of the issue that requires
            resolution
        :type description: str
        :param priority: The urgency of the request
        :type priority: SupportCasePriority,
        :param issue_type: The type of issue. If the issue is not clearly
            identifiable, use `SupportCaseIssueType.Unknown`.
        :type issue_type: SupportCaseIssueType
        :param spu_serial: The serial number of an SPU related to the support
            case.
        :type spu_serial: str, optional
        :param resource_type: The type of resource related to the support case.
        :type resource_type: ResourceType, optional
        :param resource_id: The unique identifier of the resource related to
            the support case. If ``resource_type`` is specified, also this
            parameter should be supplied.
        :type resource_id: str, optional
        """

        self.__subject = subject
        self.__description = description
        self.__priority = priority
        self.__issue_type = issue_type
        self.__spu_serial = spu_serial
        self.__resource_type = resource_type
        self.__resource_id = resource_id

    @property
    def subject(self) -> str:
        """High level summary of the support case"""
        return self.__subject

    @property
    def description(self) -> str:
        """Detailed description of the issue"""
        return self.__description

    @property
    def priority(self) -> SupportCasePriority:
        """Urgency of the support case"""
        return self.__priority

    @property
    def issue_type(self) -> SupportCaseIssueType:
        """Type of support case / issue"""
        return self.__issue_type

    @property
    def spu_serial(self) -> str:
        """Serial number of the SPU related to the support case / issue"""
        return self.__spu_serial

    @property
    def resource_type(self) -> ResourceType:
        """Type of resource related to the support case / issue"""
        return self.__resource_type

    @property
    def resource_id(self) -> str:
        """Unique identifier for the resource related to the support case"""
        return self.__resource_id

    @property
    def as_dict(self):
        result = dict()
        result["subject"] = self.subject
        result["description"] = self.description
        result["priority"] = self.priority
        result["issueType"] = self.issue_type
        result["spuSerial"] = self.spu_serial
        result["resourceType"] = self.resource_type
        result["resourceID"] = self.resource_id
        return result


class UpdateSupportCaseInput:
    """An input object to update an existing support case

    Allows updating of a support case in nebulon ON. A support case allows
    customers to get their issues associated with nebulon Cloud-Defined Storage
    to be resolved with their preferred support channel. Issues may include
    infrastructure and hardware issues, software issues, or questions.
    """

    def __init__(
            self,
            subject: str = None,
            description: str = None,
            priority: SupportCasePriority = None,
            status: SupportCaseStatus = None,
            contact_user_uuid: str = None,
            improvement_suggestion: str = None,
            comment: str = None
    ):
        """Constructs a new input object to update an existing support case

        :param subject: High level summary of an issue
        :type subject: str
        :param description: Detailed description of the issue that requires
            resolution
        :type description: str
        :param priority: The urgency of the request
        :type priority: SupportCasePriority,
        :param status: The new status of the support case. If an issue is
            resolved, use `SupportCaseStatus.Closed`.
        :type status: SupportCaseStatus
        :param contact_user_uuid: Allows changing the user contact at the
            customer that shall be contacted by support for this issue.
        :type contact_user_uuid: str, optional
        :param improvement_suggestion: Allows providing feedback to how support
            handled the support case and suggest any improvements for future
            requests.
        :type improvement_suggestion: str, optional
        :param comment: Allows specifying a comment for the support case as a
            response to a support question or to provide further details.
        :type comment: str, optional
        """
        self.__subject = subject
        self.__description = description
        self.__priority = priority
        self.__status = status
        self.__contact_user_uuid = contact_user_uuid
        self.__improvement_suggestion = improvement_suggestion
        self.__comment = comment

    @property
    def subject(self) -> str:
        """High level summary of an issue"""
        return self.__subject

    @property
    def description(self) -> str:
        """Detailed description of the issue"""
        return self.__description

    @property
    def priority(self) -> SupportCasePriority:
        """The urgency of the request"""
        return self.__priority

    @property
    def status(self) -> SupportCaseStatus:
        """The new status of the support case"""
        return self.__status

    @property
    def contact_user_uuid(self) -> str:
        """The identifier for the user to be contacted for the support case"""
        return self.__contact_user_uuid

    @property
    def improvement_suggestion(self) -> str:
        """Feedback for support for improvement"""
        return self.__improvement_suggestion

    @property
    def comment(self) -> str:
        """A comment to add to the support case history"""
        return self.__comment

    @property
    def as_dict(self):
        result = dict()
        result["subject"] = self.subject
        result["description"] = self.description
        result["priority"] = self.priority
        result["status"] = self.status
        result["contactUserUUID"] = self.contact_user_uuid
        result["improvementSuggestion"] = self.improvement_suggestion
        result["comment"] = self.comment
        return result


class SupportCaseComment:
    """A comment in the support case history

    Allows interaction between the customer and support for further
    clarification of issues or providing support case status updates. Customers
    and support can add comments to a support case for bi-directional
    communication.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new support case comment object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__time = read_value(
            "time", response, datetime, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__text = read_value(
            "text", response, str, True)

    @property
    def time(self) -> datetime:
        """The date and time when the comment was published"""
        return self.__time

    @property
    def name(self) -> str:
        """The name of the user that published the comment"""
        return self.__name

    @property
    def text(self) -> str:
        """The text contents of the comment"""
        return self.__text

    @staticmethod
    def fields():
        return [
            "time",
            "name",
            "text",
        ]


class SupportCaseContact:
    """Represents the user contact for a support case

    The support case contact is used by support to work on resolving an issue.
    By default the contact for a support case is the user that created the
    support case, but can be altered.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new support case contact object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__contact_uuid = read_value(
            "contactID", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__email = read_value(
            "email", response, str, True)
        self.__phone = read_value(
            "phone", response, str, True)
        self.__mobile = read_value(
            "mobile", response, str, True)

    @property
    def contact_uuid(self) -> str:
        """The unique identifier of the contact"""
        return self.__contact_uuid

    @property
    def name(self) -> str:
        """The name of the contact"""
        return self.__name

    @property
    def email(self) -> str:
        """The email address of the contact"""
        return self.__email

    @property
    def phone(self) -> str:
        """The phone number of the contact"""
        return self.__phone

    @property
    def mobile(self) -> str:
        """The mobile phone number of the contact"""
        return self.__mobile

    @staticmethod
    def fields():
        return [
            "contactID",
            "name",
            "email",
            "phone",
            "mobile",
        ]


class SupportCaseAttachment:
    """A file attachment to a support case

    Allows customers to attach arbitrary data to a support case. Examples are
    screenshots of the user interface, log files from application servers, or
    other supporting data for resolving a support case.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new support case attachment object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__file_name = read_value(
            "fileName", response, str, True)
        self.__upload_time = read_value(
            "uploadTime", response, datetime, True)
        self.__file_size_bytes = read_value(
            "fileSizeBytes", response, int, True)
        self.__unique_id = read_value(
            "uniqueID", response, str, True)

    @property
    def file_name(self) -> str:
        """The name of the uploaded file"""
        return self.__file_name

    @property
    def upload_time(self) -> datetime:
        """The date and time of upload"""
        return self.__upload_time

    @property
    def file_size_bytes(self) -> int:
        """The size of the file in bytes"""
        return self.__file_size_bytes

    @property
    def unique_id(self) -> str:
        """The unique identifier of the uploaded file"""
        return self.__unique_id

    @staticmethod
    def fields():
        return [
            "fileName",
            "uploadTime",
            "fileSizeBytes",
            "uniqueID",
        ]


class SupportCase:
    """A support case object in nebulon ON

    A support case is used by customers to have their issues with nebulon
    infrastructure resolved. Issues may include infrastructure and hardware
    issues, software issues, or general questions.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new support case object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__number = read_value(
            "number", response, str, True)
        self.__subject = read_value(
            "subject", response, str, True)
        self.__description = read_value(
            "description", response, str, True)
        self.__priority = read_value(
            "priority", response, SupportCasePriority, True)
        self.__issue_type = read_value(
            "issueType", response, SupportCaseIssueType, True)
        self.__status = read_value(
            "status", response, SupportCaseStatus, True)
        self.__created_date = read_value(
            "createdDate", response, datetime, True)
        self.__updated_date = read_value(
            "updatedDate", response, datetime, False)
        self.__closed_date = read_value(
            "closedDate", response, datetime, False)
        self.__contact = read_value(
            "contact", response, SupportCaseContact, False)
        self.__owner_name = read_value(
            "ownerName", response, str, True)
        self.__owner_email = read_value(
            "ownerEmail", response, str, True)
        self.__comments = read_value(
            "comments", response, SupportCaseComment, False)
        self.__attachments = read_value(
            "attachments", response, SupportCaseAttachment, False)
        self.__improvement_suggestion = read_value(
            "improvementSuggestion", response, str, True)
        self.__resource_type = read_value(
            "resourceType", response, str, True)
        self.__resource_id = read_value(
            "resourceID", response, str, True)
        self.__alert_id = read_value(
            "alertID", response, str, True)
        self.__spu_serial = read_value(
            "spuSerial", response, str, True)
        self.__kb_link = read_value(
            "kbLink", response, str, True)
        self.__oem_name = read_value(
            "oemName", response, str, True)
        self.__oem_case_number = read_value(
            "oemCaseNumber", response, str, True)
        self.__oem_created_date = read_value(
            "oemCreatedDate", response, datetime, False)
        self.__oem_updated_date = read_value(
            "oemUpdatedDate", response, datetime, False)

    @property
    def number(self) -> str:
        """Support case number"""
        return self.__number

    @property
    def subject(self) -> str:
        """High level summary of the support case / issue"""
        return self.__subject

    @property
    def description(self) -> str:
        """Detailed description of the support case / issue"""
        return self.__description

    @property
    def priority(self) -> SupportCasePriority:
        """Urgency of the support case"""
        return self.__priority

    @property
    def issue_type(self) -> SupportCaseIssueType:
        """Type of issue"""
        return self.__issue_type

    @property
    def status(self) -> SupportCaseStatus:
        """Status of the support case"""
        return self.__status

    @property
    def created_date(self) -> datetime:
        """Date and time when the support case was created"""
        return self.__created_date

    @property
    def updated_date(self) -> datetime:
        """Date and time when the support case was last updated"""
        return self.__updated_date

    @property
    def closed_date(self) -> datetime:
        """Date and time when the support case / issue was resolved"""
        return self.__closed_date

    @property
    def contact(self) -> SupportCaseContact:
        """The customer contact for the support case"""
        return self.__contact

    @property
    def owner_name(self) -> str:
        """The case owner working the support case in support"""
        return self.__owner_name

    @property
    def comments(self) -> [SupportCaseComment]:
        """List of comments for the support case"""
        return self.__comments

    @property
    def attachments(self) -> [SupportCaseAttachment]:
        """List of attachments for the support case"""
        return self.__attachments

    @property
    def improvement_suggestion(self) -> list:
        """Customer feedback for improving future requests"""
        return self.__improvement_suggestion

    @property
    def resource_type(self) -> str:
        """Associated resource type for the support case"""
        return self.__resource_type

    @property
    def resource_id(self) -> str:
        """Unique identifier of the associated resource for the support case"""
        return self.__resource_id

    @property
    def alert_id(self) -> str:
        """Unique identifier of an associated alert"""
        return self.__alert_id

    @property
    def spu_serial(self) -> str:
        """Serial number of the associated SPU for the support case"""
        return self.__spu_serial

    @property
    def kb_link(self) -> str:
        """Knowledge Base article related to this support case"""
        return self.__kb_link

    @property
    def oem_name(self) -> str:
        """Name of the server vendor associated with the infrastructure"""
        return self.__oem_name

    @property
    def oem_case_number(self) -> str:
        """Support case number with the server vendor"""
        return self.__oem_case_number

    @property
    def oem_created_date(self) -> datetime:
        """Date and time of support case creation with the server vendor"""
        return self.__oem_created_date

    @property
    def oem_updated_date(self) -> datetime:
        """Date and time of last update with the server vendor"""
        return self.__oem_updated_date

    @staticmethod
    def fields():
        return [
            "number",
            "subject",
            "description",
            "priority",
            "issueType",
            "status",
            "createdDate",
            "updatedDate",
            "closedDate",
            "contact{%s}" % (",".join(SupportCaseContact.fields())),
            "ownerName",
            "ownerEmail",
            "comments{%s}" % (",".join(SupportCaseComment.fields())),
            "attachments{%s}" % (",".join(SupportCaseAttachment.fields())),
            "improvementSuggestion",
            "resourceType",
            "resourceID",
            "alertID",
            "spuSerial",
            "kbLink",
            "oemName",
            "oemCaseNumber",
            "oemCreatedDate",
            "oemUpdatedDate",
        ]


class SupportCaseList:
    """Paginated support case list object

    Contains a list of support case objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new support case list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)
        self.__items = read_value(
            "items", response, SupportCase, True)

    @property
    def items(self) -> list:
        """List of support cases in the pagination list"""
        return self.__items

    @property
    def more(self) -> bool:
        """Indicates if there are more items on the server"""
        return self.__more

    @property
    def total_count(self) -> int:
        """The total number of items on the server"""
        return self.__total_count

    @property
    def filtered_count(self) -> int:
        """The number of items on the server matching the provided filter"""
        return self.__filtered_count

    @staticmethod
    def fields():
        return [
            "items{%s}" % (",".join(SupportCase.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class SupportCaseMixin(NebMixin):
    """Mixin to add support case related methods to the GraphQL client"""

    def get_support_cases(
            self,
            page: PageInput = None,
            sc_filter: SupportCaseFilter = None,
            sort: SupportCaseSort = None
    ) -> SupportCaseList:
        """Retrieves a list of support cases

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param sc_filter: A filter object to filter support cases on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type sc_filter: SupportCaseFilter, optional
        :param sort: A sort definition object to sort support case objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: SupportCaseSort, optional

        :returns SupportCaseList: A paginated list of support cases.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            sc_filter, "SupportCaseFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "SupportCaseSort", False)

        # make the request
        response = self._query(
            name="getSupportCases",
            params=parameters,
            fields=SupportCaseList.fields()
        )

        # convert to object
        return SupportCaseList(response)

    def create_support_case(
            self,
            subject: str,
            description: str,
            priority: SupportCasePriority,
            issue_type: SupportCaseIssueType,
            spu_serial: str = None,
            resource_type: str = None,
            resource_id: str = None
    ) -> SupportCase:
        """Allows creation of a new support case

        Depending on the type of support case the required parameters change.
        At a minimum, customers need to supply a ``subject`` that describes the
        high level summary of the issue, a ``description`` that details their
        specific problem, a ``priority`` to indicate the urgency of the request,
        and the ``issue_type`` to better route the support case to the appropriate
        subject matter expert.

        If the issue is related to a specific services processing unit (SPU) or
        resource in nebulon ON or in the customer's datacenter, ``spu_serial``,
        ``resource_type``, and ``resource_id`` shall be specified.

        :param subject: High level summary of an issue
        :type subject: str
        :param description: Detailed description of the issue that requires
            resolution
        :type description: str
        :param priority: The urgency of the request
        :type priority: SupportCasePriority,
        :param issue_type: The type of issue. If the issue is not clearly
            identifiable, use `SupportCaseIssueType.Unknown`.
        :type issue_type: SupportCaseIssueType
        :param spu_serial: The serial number of an SPU related to the support
            case.
        :type spu_serial: str, optional
        :param resource_type: The type of resource related to the support case.
        :type resource_type: ResourceType, optional
        :param resource_id: The unique identifier of the resource related to
            the support case. If ``resource_type`` is specified, also this
            parameter should be supplied.
        :type resource_id: str, optional

        :returns SupportCase: The created support case.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateSupportCaseInput(
                subject=subject,
                description=description,
                priority=priority,
                issue_type=issue_type,
                spu_serial=spu_serial,
                resource_type=resource_type,
                resource_id=resource_id
            ),
            "CreateSupportCaseInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createSupportCase",
            params=parameters,
            fields=SupportCase.fields()
        )

        # convert to object
        return SupportCase(response)

    def update_support_case(
            self,
            case_number: str,
            subject: str = None,
            description: str = None,
            priority: SupportCasePriority = None,
            status: SupportCaseStatus = None,
            contact_user_uuid: str = None,
            improvement_suggestion: str = None,
            comment: str = None
    ) -> SupportCase:
        """Allows updating an existing support case

        :param case_number: The case number of the support case to update
        :type case_number: str
        :param subject: High level summary of an issue
        :type subject: str
        :param description: Detailed description of the issue that requires
            resolution
        :type description: str
        :param priority: The urgency of the request
        :type priority: SupportCasePriority,
        :param status: The new status of the support case. If an issue is
            resolved, use `SupportCaseStatus.Closed`.
        :type status: SupportCaseStatus
        :param contact_user_uuid: Allows changing the user contact at the
            customer that shall be contacted by support for this issue.
        :type contact_user_uuid: str, optional
        :param improvement_suggestion: Allows providing feedback to how support
            handled the support case and suggest any improvements for future
            requests.
        :type improvement_suggestion: str, optional
        :param comment: Allows specifying a comment for the support case as a
            response to a support question or to provide further details.
        :type comment: str, optional

        :returns SupportCase: The updated support case.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup parameters
        parameters = dict()
        parameters["caseNumber"] = GraphQLParam(
            case_number, "String", True)
        parameters["input"] = GraphQLParam(
            UpdateSupportCaseInput(
                subject=subject,
                description=description,
                priority=priority,
                status=status,
                contact_user_uuid=contact_user_uuid,
                improvement_suggestion=improvement_suggestion,
                comment=comment
            ),
            "UpdateSupportCaseInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateSupportCase",
            params=parameters,
            fields=SupportCase.fields()
        )

        # convert to object
        return SupportCase(response)

    def upload_support_case_attachment(
            self,
            case_number: str,
            file_path: str
    ) -> SupportCase:
        """Allows uploading and attaching files to a support case

        :param case_number: The case number of the support case to update
        :type case_number: str
        :param file_path: The absolute path to the file to upload
        :type file_path: str

        :returns SupportCase: The updated support case.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup parameters
        parameters = dict()
        parameters["caseNumber"] = GraphQLParam(
            case_number, "String", True)
        parameters["attachment"] = GraphQLParam(
            file_path, "Upload", True)

        # make the request
        response = self._mutation(
            name="uploadSupportCaseAttachment",
            params=parameters,
            fields=SupportCase.fields()
        )

        # convert to object
        return SupportCase(response)
