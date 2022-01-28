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
from .common import PageInput, NebEnum, read_value
from .filters import UuidFilter, StringFilter
from .sorting import SortDirection


class CommunicationMethodType(NebEnum):
    """Defines customer communication preferences"""

    EMAIL = "Email"
    """Prefer communication via E-Mail"""

    PHONE = "Phone"
    """Prefer communication via Phone"""


class AddressInput:
    """An input object to setup an address for a datacenter

    Allows specifying a physical address for a datacenter. This information is
    used for support cases related to physical equipment in customer's
    datacenters and to allow part shipments to the provided address.
    """

    def __init__(
            self,
            house_number: str,
            address1: str,
            address2: str,
            address3: str,
            city: str,
            state_province_code: str,
            postal_code: str,
            country_code: str
    ):
        """Constructs a new address object for a datacenter

        :param house_number: The house number and letters for the address
        :type house_number: str
        :param address1: Address field 1, typically the street address
        :type address1: str
        :param address2: Address field 2, if n/a provide an empty string
        :type address2: str
        :param address3: Address field 3, if n/a provide an empty string
        :type address3: str
        :param city: City name
        :type city: str
        :param state_province_code: The state or province code if applicable
            for the specified country. If n/a provide an empty string
        :type state_province_code: str
        :param postal_code: The postal code for the address
        :type postal_code: str
        :param country_code: The country code for the address
        :type country_code: str
        """

        self.__house_number = house_number
        self.__address1 = address1
        self.__address2 = address2
        self.__address3 = address3
        self.__city = city
        self.__state_province_code = state_province_code
        self.__postal_code = postal_code
        self.__country_code = country_code

    @property
    def house_number(self) -> str:
        """House number and letters for the address"""
        return self.__house_number

    @property
    def address1(self) -> str:
        """Address field 1, typically the street address"""
        return self.__address1

    @property
    def address2(self) -> str:
        """Address field 2, if n/a provide an empty string"""
        return self.__address2

    @property
    def address3(self) -> str:
        """Address field 3, if n/a provide an empty string"""
        return self.__address3

    @property
    def city(self) -> str:
        """City name for the address"""
        return self.__city

    @property
    def state_province_code(self) -> str:
        """State or province code for the address"""
        return self.__state_province_code

    @property
    def postal_code(self) -> str:
        """Postal code for the address"""
        return self.__postal_code

    @property
    def country_code(self) -> str:
        """Country code for the address"""
        return self.__country_code

    @property
    def as_dict(self):
        result = dict()
        result["houseNumber"] = self.house_number
        result["address1"] = self.address1
        result["address2"] = self.address2
        result["address3"] = self.address3
        result["city"] = self.city
        result["stateProvinceCode"] = self.state_province_code
        result["postalCode"] = self.postal_code
        result["countryCode"] = self.country_code
        return result


class ContactInput:
    """An input object to define a datacenter contact

    Allows specifying contact information for a data center. This information
    is used to contact a customer in case of infrastructure issues and to send
    replacement parts.
    """

    def __init__(
            self,
            user_uuid: str,
            primary: bool = False,
            communication_method: CommunicationMethodType
            = CommunicationMethodType.EMAIL
    ):
        """Constructs a new contact information object

        :param user_uuid: The unique identifier of an existing user account
            in nebulon ON that should be used as a contact
        :type user_uuid: str
        :param primary: Indicates if this contact should be the primary contact
            for a datacenter.
        :type primary: bool, optional
        :param communication_method: The preferred communication type for the
            contact
        :type communication_method: CommunicationMethodType, optional
        """
        self.__user_uuid = user_uuid
        self.__primary = primary
        self.__communication_method = communication_method

    @property
    def user_uuid(self) -> str:
        """The unique identifier of a nebulon ON user account"""
        return self.__user_uuid

    @property
    def primary(self) -> bool:
        """Indicates if this contact is the primary contact for a datacenter"""
        return self.__primary

    @property
    def communication_method(self) -> CommunicationMethodType:
        """Indicates the preferred communication method for this contact"""
        return self.__communication_method

    @property
    def as_dict(self):
        result = dict()
        result["userUUID"] = self.user_uuid
        result["primary"] = self.primary
        result["communicationMethod"] = self.communication_method
        return result


class DataCenterSort:
    """A sort object for datacenters

    Allows sorting datacenters on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for datacenters

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


class DataCenterFilter:
    """A filter object to filter datacenters.

    Allows filtering for specific datacenters in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        The filter allows only one property to be specified. If filtering on
        multiple properties is needed, use the ``and_filter`` and ``or_filter``
        options to concatenate multiple filters.

        :param uuid: Filter based on datacenter unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on datacenter name
        :type name: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on datacenter unique identifier"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on datacenter name"""
        return self.__name

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
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class CreateDataCenterInput:
    """An input object to create a datacenter

    Allows the creation of a datacenter object in nebulon ON. A
    datacenter record allows customers to logically organize their
    infrastructure by physical location and associate address and contact
    information with the physical location. This is useful for effective support
    case handling and reporting purposes.
    """

    def __init__(
            self,
            name: str,
            address: AddressInput,
            contacts: [ContactInput],
            note: str = "",
    ):
        """Constructs a new input object to create a datacenter

        At least one contact with the attribute ``primary`` set to ``True`` must
        be provided. If multiple contacts are provided, exactly one contact
        must be specified as primary.

        :param name: Name for the new datacenter
        :type name: str
        :param address: The postal address for the new datacenter
        :type address: AddressInput
        :param contacts: List of contacts for the new datacenter. At least one
            contact must be provided. Exactly one contact must be marked
            as primary.
        :type contacts: [ContactInput]
        :param note: An optional note for the new datacenter
        :type note: str, optional
        """

        self.__name = name
        self.__note = note
        self.__address = address
        self.__contacts = contacts

    @property
    def name(self) -> str:
        """Name of the datacenter"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the datacenter"""
        return self.__note

    @property
    def address(self) -> AddressInput:
        """Postal address for the datacenter"""
        return self.__address

    @property
    def contacts(self) -> [ContactInput]:
        """List of contacts for the datacenter"""
        return self.__contacts

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        result["address"] = self.address
        result["contacts"] = self.contacts
        return result


class UpdateDataCenterInput:
    """An input object to update datacenter properties

    Allows updating of an existing datacenter object in nebulon ON. A
    datacenter record allows customers to logically organize their
    infrastructure by physical location and associate address and contact
    information with the physical location. This is useful for effective support
    case handling and reporting purposes.
    """

    def __init__(
            self,
            name: str = None,
            address: AddressInput = None,
            contacts: [ContactInput] = None,
            note: str = None,
    ):
        """Constructs a new input object to update a datacenter

        At least one property must be specified.

        :param name: New name for the datacenter
        :type name: str, optional
        :param address: New postal address for the datacenter
        :type address: AddressInput, optional
        :param contacts: New list of contacts for the datacenter. If provided,
            the list of contacts must have at least one contact. Exactly one
            contact must be marked as primary.
        :type contacts: [ContactInput], optional
        :param note: The new note for the datacenter. For removing the note,
            provide an empty str.
        :type note: str, optional
        """

        self.__name = name
        self.__note = note
        self.__address = address
        self.__contacts = contacts

    @property
    def name(self) -> str:
        """Name of the datacenter"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the datacenter"""
        return self.__note

    @property
    def address(self) -> AddressInput:
        """Postal address for the datacenter"""
        return self.__address

    @property
    def contacts(self) -> [ContactInput]:
        """List of contacts for the datacenter"""
        return self.__contacts

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        result["note"] = self.note
        result["address"] = self.address
        result["contacts"] = self.contacts
        return result


class DeleteDataCenterInput:
    """An input object to delete a datacenter object

    Allows additional options when deleting a datacenter. When cascade is
    set to ``True`` all child resources are deleted with the datacenter if
    no hosts are associated with the datacenter.
    """

    def __init__(
            self,
            cascade: bool
    ):
        """Constructs a new input object to delete a datacenter object

        :param cascade: If set to True any child resources are deleted with
            the datacenter if no hosts are associated with it.
        :type cascade: bool
        """

        self.__cascade = cascade

    @property
    def cascade(self) -> bool:
        """Indicates that child items shall be deleted with the datacenter"""
        return self.__cascade

    @property
    def as_dict(self):
        result = dict()
        result["cascade"] = self.cascade
        return result


class Address:
    """An address for a datacenter

    This information is used for support cases related to physical equipment
    in customer's datacenters and to allow part shipments to the provided
    address.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new address object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """

        self.__house_number = read_value(
            "houseNumber", response, str, True)
        self.__address1 = read_value(
            "address1", response, str, True)
        self.__address2 = read_value(
            "address2", response, str, True)
        self.__address3 = read_value(
            "address3", response, str, True)
        self.__city = read_value(
            "city", response, str, True)
        self.__state_province_code = read_value(
            "stateProvinceCode", response, str, True)
        self.__postal_code = read_value(
            "postalCode", response, str, True)
        self.__country_code = read_value(
            "countryCode", response, str, True)

    @property
    def house_number(self) -> str:
        """House number and letters for the address"""
        return self.__house_number

    @property
    def address1(self) -> str:
        """Address field 1, typically the street address"""
        return self.__address1

    @property
    def address2(self) -> str:
        """Address field 2"""
        return self.__address2

    @property
    def address3(self) -> str:
        """Address field 3"""
        return self.__address3

    @property
    def city(self) -> str:
        """City name for the address"""
        return self.__city

    @property
    def state_province_code(self) -> str:
        """State or province code for the address"""
        return self.__state_province_code

    @property
    def postal_code(self) -> str:
        """Postal code for the address"""
        return self.__postal_code

    @property
    def country_code(self) -> str:
        """Country code for the address"""
        return self.__country_code

    @staticmethod
    def fields():
        return [
            "houseNumber",
            "address1",
            "address2",
            "address3",
            "city",
            "stateProvinceCode",
            "postalCode",
            "countryCode",
        ]


class Contact:
    """Contact information for a datacenter

     This information is used to contact a customer in case of infrastructure
     issues and to send replacement parts.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new contact object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__user_uuid = read_value(
            "userUUID", response, str, True)
        self.__email_address = read_value(
            "emailAddress", response, str, True)
        self.__first_name = read_value(
            "firstName", response, str, True)
        self.__last_name = read_value(
            "lastName", response, str, True)
        self.__mobile_phone = read_value(
            "mobilePhone", response, str, True)
        self.__business_phone = read_value(
            "businessPhone", response, str, True)
        self.__primary = read_value(
            "primary", response, bool, True)
        self.__communication_method = read_value(
            "communicationMethod", response, CommunicationMethodType, True)

    @property
    def user_uuid(self) -> str:
        """The unique identifier of a nebulon ON user account"""
        return self.__user_uuid

    @property
    def email_address(self) -> str:
        """The email address of the contact"""
        return self.__email_address

    @property
    def first_name(self) -> str:
        """The first name of the contact"""
        return self.__first_name

    @property
    def last_name(self) -> str:
        """The last name of the contact"""
        return self.__last_name

    @property
    def mobile_phone(self) -> str:
        """The mobile phone number of the contact"""
        return self.__mobile_phone

    @property
    def business_phone(self) -> str:
        """The business phone number of the contact"""
        return self.__business_phone

    @property
    def primary(self) -> bool:
        """Indicates if this contact is the primary contact for a datacenter"""
        return self.__primary

    @property
    def communication_method(self) -> CommunicationMethodType:
        """Indicates the preferred communication method for this contact"""
        return self.__communication_method

    @staticmethod
    def fields():
        return [
            "userUUID",
            "emailAddress",
            "firstName",
            "lastName",
            "mobilePhone",
            "businessPhone",
            "primary",
            "communicationMethod",
        ]


class DataCenter:
    """A datacenter object

    A datacenter record allows customers to logically organize their
    infrastructure by physical location and associate address and contact
    information with the physical location. This is useful for effective support
    case handling and reporting purposes.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new datacenter object

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
        self.__note = read_value(
            "note", response, str, True)
        self.__address = read_value(
            "address", response, Address, True)
        self.__contacts = read_value(
            "contacts", response, Contact, False)
        self.__lab_uuids = read_value(
            "labs.uuid", response, str, False)
        self.__lab_count = read_value(
            "labCount", response, int, True)
        self.__row_count = read_value(
            "rowCount", response, int, True)
        self.__rack_count = read_value(
            "rackCount", response, int, True)
        self.__host_count = read_value(
            "hostCount", response, int, True)

    @property
    def uuid(self) -> str:
        """Unique identifier of the datacenter"""
        return self.__uuid

    @property
    def name(self) -> str:
        """Name of the datacenter"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the datacenter"""
        return self.__note

    @property
    def address(self) -> Address:
        """Postal address for the datacenter"""
        return self.__address

    @property
    def contacts(self) -> list:
        """List of contacts for the datacenter"""
        return self.__contacts

    @property
    def room_uuids(self) -> list:
        """Unique identifiers of rooms in the datacenter"""
        return self.__lab_uuids

    @property
    def room_count(self) -> int:
        """Number of rooms in the datacenter"""
        return self.__lab_count

    @property
    def row_count(self) -> int:
        """Number of rows in the datacenter"""
        return self.__row_count

    @property
    def rack_count(self) -> int:
        """Number of racks in the datacenter"""
        return self.__rack_count

    @property
    def host_count(self) -> int:
        """Number of hosts (servers) in the datacenter"""
        return self.__host_count

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "note",
            "address{%s}" % (",".join(Address.fields())),
            "contacts{%s}" % (",".join(Contact.fields())),
            "labs{uuid}",
            "labCount",
            "rowCount",
            "rackCount",
            "hostCount",
        ]


class DataCenterList:
    """Paginated datacenter list object

    Contains a list of datacenter objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new datacenter list object

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
            "items", response, DataCenter, True)

    @property
    def items(self) -> [DataCenter]:
        """List of datacenters in the pagination list"""
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
            "items{%s}" % (",".join(DataCenter.fields())),
            "more",
            "totalCount",
            "filteredCount",
        ]


class DatacentersMixin(NebMixin):
    """Mixin to add datacenter related methods to the GraphQL client"""

    def get_datacenters(
            self,
            page: PageInput = None,
            dc_filter: DataCenterFilter = None,
            sort: DataCenterSort = None
    ) -> DataCenterList:
        """Retrieves a list of datacenter objects

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param dc_filter: A filter object to filter the datacenters on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type dc_filter: DataCenterFilter, optional
        :param sort: A sort definition object to sort the datacenter objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: DataCenterSort, optional

        :returns DataCenterList: A paginated list of datacenters.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            dc_filter, "DataCenterFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "DataCenterSort", False)

        # make the request
        response = self._query(
            name="getDataCenters",
            params=parameters,
            fields=DataCenterList.fields()
        )

        # convert to object
        return DataCenterList(response)

    def create_datacenter(
            self,
            name: str,
            address: AddressInput,
            contacts: [ContactInput],
            note: str = None
    ) -> DataCenter:
        """Allows creation of a new datacenter object

        A datacenter record allows customers to logically organize their
        infrastructure by physical location and associate address and contact
        information with the physical location. This is useful for effective
        support case handling and reporting purposes.

        :param name: Name for the new datacenter
        :type name: str
        :param address: Postal address for the new datacenter
        :type address: AddressInput
        :param contacts: List of contacts for the new datacenter. At least one
            contact must be provided and exactly one contact must have the
            ``primary`` property set to ``True``.
        :type contacts: [ContactInput]
        :param note: An optional note for the new datacenter.
        :type note: str, optional

        :returns DataCenter: The new datacenter.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateDataCenterInput(
                name=name,
                note=note,
                address=address,
                contacts=contacts
            ),
            "CreateDataCenterInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createDataCenter",
            params=parameters,
            fields=DataCenter.fields()
        )

        # convert to object
        return DataCenter(response)

    def delete_datacenter(
            self,
            uuid: str,
            cascade: bool = False
    ) -> bool:
        """Allows deletion of an existing datacenter object

        The deletion of a datacenter is only possible if the datacenter has
        no hosts (servers) associated with any child items. By default,
        deletion of a datacenter is only allowed when the datacenter is not
        referenced by any rooms or if the ``cascade`` parameter is set to ``True``.

        :param uuid: The unique identifier of the datacenter to delete
        :type uuid: str
        :param cascade: If set to True any child items of the datacenter (room,
            row, rack) will automatically deleted with this request. If set
            to False or omitted and the datacenter has child objects, the
            deletion will fail with an error.
        :type cascade: bool, optional

        :returns bool: If the query was successful

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            DeleteDataCenterInput(
                cascade=cascade
            ),
            "DeleteDataCenterInput",
            False
        )

        # make the request
        response = self._mutation(
            name="deleteDataCenter",
            params=parameters,
            fields=None
        )

        # convert to object
        return response

    def update_datacenter(
            self,
            uuid: str = None,
            name: str = None,
            address: AddressInput = None,
            contacts: [ContactInput] = None,
            note: str = None
    ) -> DataCenter:
        """Allows updating properties of an existing datacenter object

        :param uuid: The unique identifier of the datacenter to update
        :type uuid: str
        :param name: New name for the datacenter
        :type name: str, optional
        :param address: New postal address for the datacenter
        :type address: AddressInput, optional
        :param contacts: New list of contacts for the datacenter. At least one
            contact must be provided and exactly one contact must have the
            ``primary`` property set to ``True`` when providing a new list.
        :type contacts: [ContactInput], optional
        :param note: A new note for the datacenter. For removing the note,
            provide an empty str.
        :type note: str, optional

        :returns DataCenter: The updated datacenter object.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            UpdateDataCenterInput(
                name=name,
                note=note,
                address=address,
                contacts=contacts
            ),
            "UpsertDataCenterInput",
            False
        )

        # make the request
        response = self._mutation(
            name="updateDataCenter",
            params=parameters,
            fields=DataCenter.fields()
        )

        # convert to object
        return DataCenter(response)
