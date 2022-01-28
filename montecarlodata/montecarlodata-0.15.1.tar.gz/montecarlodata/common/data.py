from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Union, Any

from box import Box, BoxList
from dataclasses_json import dataclass_json, LetterCase, Undefined, CatchAll


class ConnectionType(Enum):
    """
    Enumeration of connection type values from the GraphQL API
    """
    BigQuery = "BIGQUERY"
    DataLake = "DATA_LAKE"
    Hive = "HIVE"
    Redshift = "REDSHIFT"
    Snowflake = "SNOWFLAKE"


@dataclass
class MonolithResponse:
    data: Optional[Union[Box, Dict, BoxList]] = None
    errors: Optional[List[Dict]] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class OnboardingConfiguration:
    connection_options: CatchAll  # ConnectionOptions

    connection_type: str

    validation_query: Optional[str] = None
    validation_response: Optional[str] = None

    connection_query: Optional[str] = None
    connection_response: Optional[str] = None

    warehouse_type: Optional[str] = None
    warehouse_name: Optional[str] = None

    job_limits: Optional[Dict] = None
    job_types: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class ConnectionOptions:
    monolith_base_payload: CatchAll  # Base options passed to the monolith (e.g. host, db, etc.)

    # Client connection options
    dc_id: Optional[str] = None
    validate_only: Optional[bool] = False
    skip_validation: Optional[bool] = False
    skip_permission_tests: Optional[bool] = False
    auto_yes: Optional[bool] = False

    monolith_connection_payload: dict = field(init=False)  # Additional options passed to the monolith (from client)

    def __post_init__(self):
        self.monolith_connection_payload = {}

        if self.dc_id:
            self.dc_id = str(self.dc_id)
            self.monolith_connection_payload['dcId'] = self.dc_id
        if self.skip_validation:
            self.monolith_connection_payload['skipValidation'] = self.skip_validation
        if self.skip_permission_tests:
            self.monolith_connection_payload['skipPermissionTests'] = self.skip_permission_tests


@dataclass
class ValidationResult:
    has_warnings: bool
    credentials_key: str


@dataclass
class AWSArn:
    id: str

    # components
    arn: str = field(init=False)
    partition: str = field(init=False)
    service: str = field(init=False)
    region: str = field(init=False)
    account: str = field(init=False)
    resource: str = field(init=False)
    resource_type: Optional[str] = field(init=False)

    def __post_init__(self):
        elements = self.id.split(':', 5)
        self.arn = elements[0]
        self.partition = elements[1]
        self.service = elements[2]
        self.region = elements[3]
        self.account = elements[4]
        self.resource = elements[5]
        self.resource_type = None

        if '/' in self.resource:
            self.resource_type, self.resource = self.resource.split('/', 1)
        elif ':' in self.resource:
            self.resource_type, self.resource = self.resource.split(':', 1)


@dataclass
class EventProperties:
    event_type: str

    bucket_name: str
    bucket_arn: str = field(init=False)

    event_queue_arn: str
    event_queue_name: str = field(init=False)

    collection_region: str
    cust_resources_region: str

    collection_account_id: str
    cust_account_id: str

    collection_client: Any
    cust_resources_client: Any

    topic_arn: Optional[str] = None
    topic_name: Optional[str] = None

    prefix: Optional[str] = None
    suffix: Optional[str] = None

    def __post_init__(self):
        self.bucket_arn = f'arn:aws:s3:::{self.bucket_name}'
        self.event_queue_name = AWSArn(self.event_queue_arn).resource


@dataclass
class DcResourceProperties:
    collector_arn: AWSArn
    collector_props: Box

    collection_region: str
    resources_region: str

    collection_client: Any
    resources_client: Any

    resource_arn: Optional[AWSArn] = None
    resource_props: Optional[Box] = None
