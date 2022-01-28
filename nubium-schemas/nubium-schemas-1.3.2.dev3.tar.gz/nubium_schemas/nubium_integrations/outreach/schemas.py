from nubium_schemas import pdc, AvroModel

@pdc
class OutreachProspectToUpsert(AvroModel):

    class Meta:
        schema_doc = False

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    work_phone: str = ""
    mobile_phone: str = ""
    company: str = ""
    occupation: str = ""
    address_street: str = ""
    address_street2: str = ""
    address_city: str = ""
    address_state: str = ""
    address_zip: str = ""
    address_country: str = ""
    prospect_id: str = ""
    eloqua_contact_id: str = ""
    is_subscribed: str = ""

outreach_prospect_to_upsert = OutreachProspectToUpsert.avro_schema_to_python()
