import typing
from nubium_schemas import dc, pdc, AvroModel

from .schema_components import (
    PersonalFacts,
    MarketingDescriptors,
    Privacy,
    LastSubmission,
    TrackingIds,
    Tombstone)


@pdc
class PersonSchema(AvroModel):
    personal_facts: PersonalFacts = dc.field(default_factory=PersonalFacts)
    marketing_descriptors: MarketingDescriptors = dc.field(default_factory=MarketingDescriptors)
    privacy: Privacy = dc.field(default_factory=Privacy)
    last_submission: LastSubmission = dc.field(default_factory=LastSubmission)
    tracking_ids: TrackingIds = dc.field(default_factory=TrackingIds)
    tombstone: Tombstone = dc.field(default_factory=Tombstone)
    last_evaluated_by_dwm: str = ''

    class Meta:
        schema_doc = False
        alias_nested_items = {
            "personal_facts": "PersonalFacts",
            "marketing_descriptors": "MarketingDescriptors",
            "privacy": "Privacy",
            "last_submission": "LastSubmission",
            "tracking_ids": "TrackingIds",
            "tombstone": "Tombstone"
        }


def person_empty_dict():
    return PersonSchema(**{"personal_facts": {"email_address": ""}}).asdict()


person_schema = PersonSchema.avro_schema_to_python()




@pdc
class SalesforceStreamEvent(AvroModel):
    event_replay_id: str = ""
    event_timestamp: str = ""
    event_type: str = ""
    salesforce_object_type: str = ""
    soql_query_fields: typing.Dict[str, str] = dc.field(default_factory=dict)

    class Meta:
        schema_doc = False


salesforce_stream_event = SalesforceStreamEvent.avro_schema_to_python()
