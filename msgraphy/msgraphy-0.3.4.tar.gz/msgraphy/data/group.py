from datetime import datetime
from typing import List

from msgraphy.data import graphdataclass


@graphdataclass
class Group():
    id: str
    allow_external_senders: bool = None
    classification: str = None
    creation_options: List[str] = None
    created_date_time: datetime = None
    deleted_date_time: datetime = None
    description: str = None
    display_name: str = None
    expiration_date_time: datetime = None
    group_types: List[str] = None
    is_assignable_to_role: bool = None
    mail_enabled: bool = None
    mail_nickname: str = None
    mail: str = None
    membership_rule: str = None
    membership_rule_processing_state: str = None
    on_premises_domain_name: str = None
    on_premises_last_sync_date_time: datetime = None
    on_premises_net_bios_name: str = None
    on_premises_provisioning_errors: List = None
    on_premises_sam_account_name: str = None
    on_premises_security_identifier: str = None
    on_premises_sync_enabled: bool = None
    preferred_data_location: str = None
    preferred_language: str = None
    proxy_addresses: List[str] = None
    renewed_date_time: datetime = None
    resource_behavior_options: List[str] = None
    resource_provisioning_options: List[str] = None
    security_enabled: bool = None
    security_identifier: str = None
    theme: str = None
    visibility: bool = None

