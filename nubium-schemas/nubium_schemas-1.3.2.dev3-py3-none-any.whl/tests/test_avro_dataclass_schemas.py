from nubium_schemas.campaign_response import Canon
from nubium_schemas.campaign_response.schema_components import CampaignResponse, TrackingIds 


def test_data_models_can_generate_default_dictionaries():
    expected = {
        "campaign_response": {
            "email_address": "",
            "ext_tactic_id": "",
            "int_tactic_id": "",
            "offer_consumption_timestamp": "",
            "offer_id": "",
        },
        "raw_formdata": {},
        "tracking_ids": {
            "eloqua_contacts_inquiries_id": "",
            "sfdc_contact_id": "",
            "sfdc_ext_tactic_contact_id": "",
            "sfdc_ext_tactic_lead_id": "",
            "sfdc_int_tactic_contact_id": "",
            "sfdc_int_tactic_lead_id": "",
            "sfdc_lead_id": "",
            "sfdc_offer_contact_id": "",
            "sfdc_offer_lead_id": "",
        },
    }
    assert Canon().asdict() == expected


def test_data_models_can_generate_avro_schema_in_python_dict_form():
    old_canon = {
        "name": "Canon",
        "type": "record",
        "fields": [
            {"name": "campaign_response", "type": CampaignResponse.avro_schema_to_python()},
            {"name": "tracking_ids", "type": TrackingIds.avro_schema_to_python()},
            {"name": "raw_formdata", "type": {"name": "raw_formdatum", "type": "map", "values": "string"}, "default": {}}
         ]
    }
    assert Canon.avro_schema_to_python() == old_canon
