from nubium_schemas import pdc, AvroModel

@pdc
class CampaignResponse(AvroModel):
    class Meta:
        schema_doc = False

    email_address: str = ""
    ext_tactic_id: str = ""
    int_tactic_id: str = ""
    offer_id: str = ""
    offer_consumption_timestamp: str = ""


@pdc
class TrackingIds(AvroModel):
    class Meta:
        schema_doc = False

    eloqua_contacts_inquiries_id: str = ""
    sfdc_contact_id: str = ""
    sfdc_lead_id: str = ""
    sfdc_ext_tactic_lead_id: str = ""
    sfdc_int_tactic_lead_id: str = ""
    sfdc_offer_lead_id: str = ""
    sfdc_ext_tactic_contact_id: str = ""
    sfdc_int_tactic_contact_id: str = ""
    sfdc_offer_contact_id: str = ""


@pdc
class SalesforceCampaignMember(AvroModel):
    class Meta:
        schema_doc = False

    campaign_membership_id: str = ""
    campaign_id: str = ""
    related_campaign_id: str = ""
    sfdc_contact_id: str = ""
    sfdc_lead_id: str = ""
    true_response_date: str = ""
    status: str = ""
    campaign_member_type: str = ""
