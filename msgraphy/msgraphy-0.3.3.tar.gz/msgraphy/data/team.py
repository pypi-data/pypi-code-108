from datetime import datetime

from msgraphy.data import graphdataclass


@graphdataclass
class Team:
    display_name: str = None
    description: str = None
    classification: str = None
    specialization = None
    visibility = None
    fun_settings = None
    guest_settings = None
    internal_id: str = None
    is_archived: bool = None
    member_settings = None
    messaging_settings = None
    web_url: str = None
    created_date_time: datetime = None


@graphdataclass
class Channel:
    id: str = None
    display_name: str = None
    description: str = None
    is_favourite_by_default: bool = None
    email: str = None
    web_url: str = None
    membership_type = None
    created_date_time: datetime = None
