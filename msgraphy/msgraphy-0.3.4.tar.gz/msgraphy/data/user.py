from datetime import datetime
from typing import List
from msgraphy.data import graphdataclass


@graphdataclass
class User:
    id: str = None
    account_enabled: bool = None
    business_phones: List[str] = None
    display_name: str = None
    given_name: str = None
    job_title: str = None
    mail: str = None
    mobile_phone: str = None
    office_location: str = None
    preferred_language: str = None
    surname: str = None
    user_principal_name: str = None

    # Extended - only with $select
    assigned_licenses: List = None
    license_assignment_states: List = None
    user_type: str = None
    external_user_state: str = None
    show_in_address_list: bool = None
    last_password_change_date_time: datetime = None


@graphdataclass
class UserList:
    value: List[User]
