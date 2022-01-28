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


from .graphqlclient import GraphQLParam, NebMixin
from .common import PageInput, read_value
from .filters import StringFilter, UuidFilter
from .sorting import SortDirection


class WebHookSort:
    """A sort object for webhooks

    Allows sorting webhooks on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for webhooks

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        """
        self.__name = name

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property"""
        return self.__name

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        return result


class WebHookFilter:
    """A filter object to filter webhooks.

    Allows filtering for specific webhooks in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            url: StringFilter = None,
            enabled: bool = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on webhook unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on webhook name
        :type name: StringFilter, optional
        :param url: Filter based on webhook url
        :type url: StringFilter, optional
        :param enabled: Filter based on webhook enablement status
        :type enabled: bool, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__url = url
        self.__enabled = enabled
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on datacenter unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on webhook name"""
        return self.__name

    @property
    def url(self) -> StringFilter:
        """Filter based on webhook url"""
        return self.__url

    @property
    def enabled(self) -> bool:
        """Filter based on enablement status"""
        return self.__enabled

    @property
    def and_filter(self):
        """Allows concatenation of multiple filters via logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation of multiple filters via logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["uuid"] = self.uuid
        result["name"] = self.name
        result["url"] = self.url
        result["enabled"] = self.enabled
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class HeaderInput:
    """An input object for an HTTP header

    Allows specifying custom HTTP headers for the webhook. Some services use
    custom HTTP headers for authentication or for specifying custom information.
    """

    def __init__(
            self,
            name: str,
            value: str
    ):
        """Constructs a new input object for an HTTP header

        Allows specifying custom HTTP headers for the webhook. Some
        services use custom HTTP headers for authentication or for
        specifying custom information.

        :param name: HTTP header name
        :type name: str
        :param value: HTTP header value
        :type value: str
        """

        self.__name = name
        self.__value = value

    @property
    def name(self) -> str:
        """HTTP header name"""
        return self.__name

    @property
    def value(self) -> str:
        """HTTP header value"""
        return self.__value

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["value"] = self.value
        return result


class CreateWebHookInput:
    """Input object for creating a new webhook

    Webhooks allow integration with notification services and workflow engines.
    When configured, webhooks are triggered for opened and closed alerts with
    the specified webhook payload.

    Credentials can be specified in url field or headers field. Special
    variables can be used to specify credentials without storing them in
    clear text. `$USERNAME`, `$PASSWORD`, `$AUTH_TOKEN` will be populated
    during the execution of the webhook.

    To identify open and close action for the alert, use `$ALERT_INCIDENT_ID`
    variable. The full list of available variables that are populated during
    webhook execution are:

    * `$ALERT_INCIDENT_ID` - ID of the alert incident (open and close events)
    * `$ALERT_EVENT_ID` - ID of open/close event for the alert
    * `$ALERT_CODE` - Code of the alert
    * `$ALERT_SUMMARY` - Summary of the alert status
    * `$ALERT_STATUS` - status of the alert
    * `$ALERT_DETAILS` - Full details of the alert
    * `$ALERT_TIME` - Formatted time of when alert was created
    * `$ALERT_URL` - URL of the alert, e.g.: https://on.nebulon.com/alert/{uuid}
    * `$ALERT_SEVERITY` - Severity of the event (e.g. trivial, minor, etc.)
    * `$RESOURCE_TYPE` - Type of the resource that alert is for
    * `$RESOURCE_ID` - ID of the resource that alert is for
    * `$RESOURCE_NAME` - Name of the resource that alert is for
    * `$HOST_NAME` - Host name (if known) of the server in question
    * `$HOST_SERIAL` - Host serial (if known) of the server in question
    * `$HOST_MANUF` - Host manufacturer of the server in question
    * `$SPU_SERIAL` - SPU serial number related to the described alert
    * `$NPOD_UUID` - nPod UUID related to the described alert (if present)
    * `$NPOD_NAME` - nPod name related to the described alert (if present)
    * `$ORG_UUID` - Org UUID related to the alert
    * `$ORG_NAME` - Organization name related to the alert
    * `$CONTACT_EMAIL` - Email address of contact for the datacenter
    """

    def __init__(
            self,
            name: str,
            open_url: str = None,
            close_url: str = None,
            open_body: str = None,
            close_body: str = None,
            username: str = None,
            password: str = None,
            auth_token: str = None,
            headers: [HeaderInput] = None,
            time_zone: str = "UTC",
            enabled: bool = None
    ):
        """Constructs an input object to create a new webhook

        Webhooks allow integration with notification services and workflow
        engines. When configured, webhooks are triggered for opened and closed
        alerts with the specified webhook payload.

        :param name: Human readable name for the webhook
        :type name: str
        :param open_url: The URL for the webhook that is called for open alert
            events. Either open_url, close_url or both can be specified.
        :type open_url: str, optional
        :param close_url: The URL for the webhook that is called for close
            alert events. Either open_url, close_url or both can be specified.
        :type close_url: str, optional
        :param open_body: The main body of the webhook as a JSON string for
            open alert events. This body is sent to the URL specified in
            ``open_url``.
        :type open_body: str, optional
        :param close_body: The main body of the webhook as a JSON string for
            close alert events. This body is sent to the URL specified in
            ``close_url``.
        :type close_body: str, optional
        :param username: If username and password are used for authenticating
            with the target URL, use the username field. This will populate
            the `$USERNAME` variable
        :type username: str, optional
        :param password: If username and password are used for authenticating
            with the target URL, use the password field. This will populate
            the `$USERNAME` variable
        :type password: str, optional
        :param auth_token: If an authentication token is used with the webhook
            use auth_token. This will populate the `$AUTH_TOKEN` variable.
        :type auth_token: str, optional
        :param headers: List of HTTP headers for the request
        :type headers: [HeaderInput], optional
        :param time_zone: The timezone to use when formatting time stings in
            the webhook. If not specified
        :type time_zone: str, optional
        :param enabled: Allows specifying if the webhook shall be enabled or
            disabled after creation. If not specified, the webhook will be
            enabled by default.
        :type enabled: bool, optional
        """
        self.__name = name
        self.__open_url = open_url
        self.__close_url = close_url
        self.__username = username
        self.__password = password
        self.__auth_token = auth_token
        self.__headers = headers
        self.__open_body = open_body
        self.__close_body = close_body
        self.__time_zone = time_zone
        self.__enabled = enabled

    @property
    def name(self) -> str:
        """Human readable name for the webhook"""
        return self.__name

    @property
    def open_url(self) -> str:
        """Webhook URL that is called for open alert events"""
        return self.__open_url

    @property
    def close_url(self) -> str:
        """Webhook URL that is called for close alert events"""
        return self.__close_url

    @property
    def username(self) -> str:
        """Username field that populates the `$USERNAME` variable"""
        return self.__username

    @property
    def password(self) -> str:
        """Password field that populates the `$PASSWORD` variable"""
        return self.__password

    @property
    def auth_token(self) -> str:
        """Auth token field that populates the `$AUTH_TOKEN` variable"""
        return self.__auth_token

    @property
    def headers(self) -> [HeaderInput]:
        """List of HTTP headers to send with the request"""
        return self.__headers

    @property
    def open_body(self) -> str:
        """JSON encoded string that is sent to the ``open_url`` URL"""
        return self.__open_body

    @property
    def close_body(self) -> str:
        """JSON encoded string that is sent to the ``close_url`` URL"""
        return self.__close_body

    @property
    def time_zone(self) -> str:
        """Time zone that is used to format date and time strings"""
        return self.__time_zone

    @property
    def enabled(self) -> bool:
        """Specifies if the webhook is enabled or disabled"""
        return self.__enabled

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["openURL"] = self.open_url
        result["closeURL"] = self.close_url
        result["username"] = self.username
        result["password"] = self.password
        result["authToken"] = self.auth_token
        result["headers"] = self.headers
        result["openBody"] = self.open_body
        result["closeBody"] = self.close_body
        result["timeZone"] = self.time_zone
        return result


class UpdateWebHookInput:
    """Input object for updating a new webhook

    Webhooks allow integration with notification services and workflow engines.
    When configured, webhooks are triggered for opened and closed alerts with
    the specified webhook payload.

    Credentials can be specified in url field or headers field. Special
    variables can be used to specify credentials without storing them in
    clear text. `$USERNAME`, `$PASSWORD`, `$AUTH_TOKEN` will be populated
    during the execution of the webhook.

    To identify open and close action for the alert, use `$ALERT_INCIDENT_ID`
    variable. The full list of available variables that are populated during
    webhook execution are:

    * `$ALERT_INCIDENT_ID` - ID of the alert incident (open and close events)
    * `$ALERT_EVENT_ID` - ID of open/close event for the alert
    * `$ALERT_CODE` - Code of the alert
    * `$ALERT_SUMMARY` - Summary of the alert status
    * `$ALERT_STATUS` - status of the alert
    * `$ALERT_DETAILS` - Full details of the alert
    * `$ALERT_TIME` - Formatted time of when alert was created
    * `$ALERT_URL` - URL of the alert, e.g.: https://on.nebulon.com/alert/{uuid}
    * `$ALERT_SEVERITY` - Severity of the event (e.g. trivial, minor, etc.)
    * `$RESOURCE_TYPE` - Type of the resource that alert is for
    * `$RESOURCE_ID` - ID of the resource that alert is for
    * `$RESOURCE_NAME` - Name of the resource that alert is for
    * `$HOST_NAME` - Host name (if known) of the server in question
    * `$HOST_SERIAL` - Host serial (if known) of the server in question
    * `$HOST_MANUF` - Host manufacturer of the server in question
    * `$SPU_SERIAL` - SPU serial number related to the described alert
    * `$NPOD_UUID` - nPod UUID related to the described alert (if present)
    * `$NPOD_NAME` - nPod name related to the described alert (if present)
    * `$ORG_UUID` - Org UUID related to the alert
    * `$ORG_NAME` - Organization name related to the alert
    * `$CONTACT_EMAIL` - Email address of contact for the datacenter
    """

    def __init__(
            self,
            name: str = None,
            open_url: str = None,
            close_url: str = None,
            open_body: str = None,
            close_body: str = None,
            username: str = None,
            password: str = None,
            auth_token: str = None,
            headers: [HeaderInput] = None,
            time_zone: str = None,
            enabled: bool = None
    ):
        """Constructs an input object to update a new webhook

        Webhooks allow integration with notification services and workflow
        engines. When configured, webhooks are triggered for opened and closed
        alerts with the specified webhook payload.

        :param name: Human readable name for the webhook
        :type name: str, optional
        :param open_url: The URL for the webhook that is called for open alert
            events. Either open_url, close_url or both can be specified.
        :type open_url: str, optional
        :param close_url: The URL for the webhook that is called for close
            alert events. Either open_url, close_url or both can be specified.
        :type close_url: str, optional
        :param open_body: The main body of the webhook as a JSON string for
            open alert events. This body is sent to the URL specified in
            ``open_url``.
        :type open_body: str, optional
        :param close_body: The main body of the webhook as a JSON string for
            close alert events. This body is sent to the URL specified in
            ``close_url``.
        :type close_body: str, optional
        :param username: If username and password are used for authenticating
            with the target URL, use the username field. This will populate
            the `$USERNAME` variable
        :type username: str, optional
        :param password: If username and password are used for authenticating
            with the target URL, use the password field. This will populate
            the `$USERNAME` variable
        :type password: str, optional
        :param auth_token: If an authentication token is used with the webhook
            use auth_token. This will populate the `$AUTH_TOKEN` variable.
        :type auth_token: str, optional
        :param headers: List of HTTP headers for the request
        :type headers: [HeaderInput], optional
        :param time_zone: The timezone to use when formatting time stings in
            the webhook. If not specified
        :type time_zone: str, optional
        :param enabled: Allows specifying if the webhook shall be enabled or
            disabled after creation. If not specified, the webhook will be
            enabled by default.
        :type enabled: bool, optional
        """

        self.__name = name
        self.__open_url = open_url
        self.__close_url = close_url
        self.__username = username
        self.__password = password
        self.__auth_token = auth_token
        self.__headers = headers
        self.__open_body = open_body
        self.__close_body = close_body
        self.__time_zone = time_zone
        self.__enabled = enabled

    @property
    def name(self) -> str:
        """Human readable name for the webhook"""
        return self.__name

    @property
    def open_url(self) -> str:
        """Webhook URL that is called for open alert events"""
        return self.__open_url

    @property
    def close_url(self) -> str:
        """Webhook URL that is called for close alert events"""
        return self.__close_url

    @property
    def username(self) -> str:
        """Username field that populates the `$USERNAME` variable"""
        return self.__username

    @property
    def password(self) -> str:
        """Password field that populates the `$PASSWORD` variable"""
        return self.__password

    @property
    def auth_token(self) -> str:
        """Auth token field that populates the `$AUTH_TOKEN` variable"""
        return self.__auth_token

    @property
    def headers(self) -> [HeaderInput]:
        """List of HTTP headers to send with the request"""
        return self.__headers

    @property
    def open_body(self) -> str:
        """JSON encoded string that is sent to the ``open_url`` URL"""
        return self.__open_body

    @property
    def close_body(self) -> str:
        """JSON encoded string that is sent to the ``close_url`` URL"""
        return self.__close_body

    @property
    def time_zone(self) -> str:
        """Time zone that is used to format date and time strings"""
        return self.__time_zone

    @property
    def enabled(self) -> bool:
        """Specifies if the webhook is enabled or disabled"""
        return self.__enabled

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["openURL"] = self.open_url
        result["closeURL"] = self.close_url
        result["username"] = self.username
        result["password"] = self.password
        result["authToken"] = self.auth_token
        result["headers"] = self.headers
        result["openBody"] = self.open_body
        result["closeBody"] = self.close_body
        result["timeZone"] = self.time_zone
        return result


class TestWebHookInput:
    """Input object for testing webhooks"""

    def __init__(
            self,
            uuid: str = None,
            create: CreateWebHookInput = None,
            update: UpdateWebHookInput = None,
    ):
        """Constructs a new TestWebHookInput object

        Allows testing existing, new, or updates to webhooks before they are
        permanently stored in the cloud. When ``create`` is specified, neither
        ``uuid`` or ``update`` should be specified.

        :param uuid: The unique identifier of an existing webhook that shall
            be tested. Optionally, ``update`` can be specified when testing
            changes to the existing webhook.
        :type uuid: str, optional
        :param create: The definition for a new webhook to be tested. If this
            parameter is provided, neither ``uuid`` or ``update`` must be specified.
        :type create: CreateWebHookInput, optional
        :param update: The update definition for an existing webhook. If this
            parameter is provided, also ``uuid`` is required.
        :type update: UpdateWebHookInput, optional
        """

        self.__uuid = uuid
        self.__create = create
        self.__update = update

    @property
    def uuid(self) -> str:
        """The unique identifier of the webhook to be tested"""
        return self.__uuid

    @property
    def create(self) -> CreateWebHookInput:
        """A definition for a new webhook to be tested"""
        return self.__create

    @property
    def update(self) -> UpdateWebHookInput:
        """A definition for the updates for a webhook to be tested"""
        return self.__update

    @property
    def as_dict(self):
        result = dict()
        result["uuid"] = self.uuid
        result["create"] = self.create
        result["update"] = self.update
        return result


class TestWebHookResponse:
    """Response for when testing a webhook"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new TestWebHookResponse object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__failed = read_value(
            "failed", response, bool, True)
        self.__open_error_message = read_value(
            "openErrorMessage", response, str, True)
        self.__close_error_message = read_value(
            "closeErrorMessage", response, str, True)

    @property
    def failed(self) -> bool:
        """Indicates if the test webhook call failed"""
        return self.__failed

    @property
    def open_error_message(self) -> str:
        """Error message when testing the webhook with the ``open_url``"""
        return self.__open_error_message

    @property
    def close_error_message(self) -> str:
        """Error message when testing the webhook with the ``close_url``"""
        return self.__close_error_message

    @staticmethod
    def fields():
        return [
            "failed",
            "openErrorMessage",
            "closeErrorMessage",
        ]


class Header:
    """HTTP Header object"""

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new HTTP header object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__name = read_value(
            "name", response, str, True)
        self.__value = read_value(
            "value", response, str, True)

    @property
    def name(self) -> str:
        """HTTP header name"""
        return self.__name

    @property
    def value(self) -> str:
        """HTTP header value"""
        return self.__value

    @staticmethod
    def fields():
        return [
            "name",
            "value",
        ]


class WebHook:
    """Webhook instance object

    Webhooks allow integration with notification services and workflow engines.
    When configured, webhooks are triggered for opened and closed alerts with
    the specified webhook payload.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new WebHook object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__open_url = read_value(
            "openURL", response, str, True)
        self.__close_url = read_value(
            "closeURL", response, str, True)
        self.__headers = read_value(
            "headers", response, list, False)
        self.__open_body = read_value(
            "openBody", response, str, True)
        self.__close_body = read_value(
            "closeBody", response, str, True)
        self.__enabled = read_value(
            "enabled", response, bool, True)
        self.__time_zone = read_value(
            "timeZone", response, str, True)
        self.__errors = read_value(
            "errors", response, bool, True)
        self.__last_open_error = read_value(
            "lastOpenError", response, str, True)
        self.__last_close_error = read_value(
            "lastCloseError", response, str, True)

    @property
    def uuid(self) -> str:
        return self.__uuid

    @property
    def name(self) -> str:
        return self.__name

    @property
    def open_url(self) -> str:
        return self.__open_url

    @property
    def close_url(self) -> str:
        return self.__close_url

    @property
    def headers(self) -> list:
        return self.__headers

    @property
    def open_body(self) -> str:
        return self.__open_body

    @property
    def close_body(self) -> str:
        return self.__close_body

    @property
    def enabled(self) -> bool:
        return self.__enabled

    @property
    def time_zone(self) -> str:
        return self.__time_zone

    @property
    def errors(self) -> bool:
        return self.__errors

    @property
    def last_open_error(self) -> str:
        return self.__last_open_error

    @property
    def last_close_error(self) -> str:
        return self.__last_close_error

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "openURL",
            "closeURL",
            "headers{%s}" % ",".join(Header.fields()),
            "openBody",
            "closeBody",
            "enabled",
            "timeZone",
            "errors",
            "lastOpenError",
            "lastCloseError",
        ]


class WebHookList:
    """Paginated webhook list object

    Contains a list of webhook objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new webhook list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, WebHook, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> [WebHook]:
        """List of webhooks in the pagination list"""
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
            "items{%s}" % ",".join(WebHook.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class WebHookMixin(NebMixin):
    """Mixin to add webhook related functions to the GraphQL client"""

    def get_webhooks(
            self,
            page: PageInput = None,
            wh_filter: WebHookFilter = None,
            sort: WebHookSort = None,
    ) -> WebHookList:
        """Retrieves a list of webhooks

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param wh_filter: A filter object to filter the webhooks on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type wh_filter: WebHookFilter, optional
        :param sort: A sort definition object to sort the webhook objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: WebHookSort, optional

        :returns WebHookList: A paginated list of webhooks.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            wh_filter, "WebHookFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "WebHookSort", False)

        # make the request
        response = self._query(
            name="getWebHooks",
            params=parameters,
            fields=WebHookList.fields()
        )

        # convert to object
        return WebHookList(response)

    def create_webhook(
            self,
            definition: CreateWebHookInput
    ) -> WebHook:
        """Creates a new webhook

        Webhooks allow integration with notification services and workflow
        engines. When configured, webhooks are triggered for opened and closed
        alerts with the specified webhook payload.

        :param definition: The definition for a new webhook
        :type definition: CreateWebHookInput
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            definition,
            "CreateWebHookInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createWebHook",
            params=parameters,
            fields=WebHook.fields()
        )

        # convert to object
        return WebHook(response)

    def update_webhook(
            self,
            uuid: str,
            updates: UpdateWebHookInput
    ) -> WebHook:
        """Updates an existing webhook

        Webhooks allow integration with notification services and workflow
        engines. When configured, webhooks are triggered for opened and closed
        alerts with the specified webhook payload.

        :param uuid: The unique identifier of the webhook to update
        :type uuid: str
        :param updates: The definition for updates to be made for the webhook
        :type updates: UpdateWebHookInput
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            updates,
            "UpdateWebHookInput",
            True
        )

        # make the request
        response = self._mutation(
            name="updateWebHook",
            params=parameters,
            fields=WebHook.fields()
        )

        # convert to object
        return WebHook(response)

    def delete_webhook(
            self,
            uuid: str
    ) -> bool:
        """Deletes an existing webhook

        :param uuid: The unique identifier of the webhook to delete
        :type uuid: str
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)

        # make the request
        response = self._mutation(
            name="deleteWebHook",
            params=parameters,
            fields=None
        )

        # response is a boolean
        return response

    def test_webhook(
            self,
            uuid: str = None,
            create: CreateWebHookInput = None,
            update: UpdateWebHookInput = None
    ) -> TestWebHookResponse:
        """Test a webhook

        Allows testing existing, new, or updates to webhooks before they are
        permanently stored in the cloud. When ``create`` is specified, neither
        ``uuid`` or ``update`` should be specified.

        :param uuid: The unique identifier of an existing webhook that shall
            be tested. Optionally, ``update`` can be specified when testing
            changes to the existing webhook.
        :type uuid: str, optional
        :param create: The definition for a new webhook to be tested. If this
            parameter is provided, neither ``uuid`` or ``update`` must be specified.
        :type create: CreateWebHookInput, optional
        :param update: The update definition for an existing webhook. If this
            parameter is provided, also ``uuid`` is required.
        :type update: UpdateWebHookInput, optional
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            TestWebHookInput(
                uuid=uuid,
                create=create,
                update=update
            ),
            "TestWebHookInput",
            True)

        # make the request
        response = self._mutation(
            name="testWebHook",
            params=parameters,
            fields=TestWebHookResponse.fields()
        )

        # convert to object
        return TestWebHookResponse(response)
