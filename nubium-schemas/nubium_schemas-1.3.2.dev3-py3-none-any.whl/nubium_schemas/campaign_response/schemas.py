import typing
from nubium_schemas import dc, pdc, AvroModel
from .schema_components import CampaignResponse, TrackingIds, SalesforceCampaignMember


@pdc
class Canon(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "campaign_response": "CampaignResponse",
            "tracking_ids": "TrackingIds",
        }

    campaign_response: CampaignResponse = dc.field(default_factory=CampaignResponse)
    tracking_ids: TrackingIds = dc.field(default_factory=TrackingIds)
    raw_formdata: typing.Dict[str, str] = dc.field(default_factory=dict)


canon = Canon.avro_schema_to_python()

@pdc
class CampaignMembersCreate(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "campaign_response": "CampaignResponse",
            "tracking_ids": "TrackingIds",
        }

    campaign_response: CampaignResponse = dc.field(default_factory=CampaignResponse)
    tracking_ids: TrackingIds = dc.field(default_factory=TrackingIds)
    campaign_members_to_create: typing.List[typing.Union[SalesforceCampaignMember, None]] = dc.field(default_factory=lambda: [SalesforceCampaignMember().asdict()])


campaign_members_create = CampaignMembersCreate.avro_schema_to_python()

@pdc
class CampaignMembersUpdate(AvroModel):
    class Meta:
        schema_doc = False

    campaign_members_to_update: typing.List[typing.Union[SalesforceCampaignMember, None]] = dc.field(default_factory=lambda: [SalesforceCampaignMember().asdict()])


campaign_members_update = CampaignMembersUpdate.avro_schema_to_python()
