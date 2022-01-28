import typing
from nubium_schemas import dc, pdc, AvroModel

@pdc
class Address(AvroModel):
    class Meta:
        schema_doc = False

    country_name: str = ""
    country_code: str = ""
    address_street_1: str = ""
    address_street_2: str = ""
    address_street_3: str = ""
    address_city: str = ""
    address_state_province: str = ""
    address_postal_code: str = ""
    core_based_statistical_area: str = ""
    combined_statistical_area: str = ""


@pdc
class Job(AvroModel):
    class Meta:
        schema_doc = False

    company: str = ""
    business_phone: str = ""
    job_title: str = ""
    department: str = ""
    job_role: str = ""
    job_level: str = ""
    job_function: str = ""
    industry: str = ""
    annual_revenue: str = ""
    company_size: str = ""


@pdc
class PersonalFacts(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "address": "Address",
            "job": "Job",
        }

    email_address: str
    salutation: str = ""
    first_name: str = ""
    last_name: str = ""
    mobile_phone: str = ""
    language_preference: str = ""
    address: Address = dc.field(default_factory=Address)
    job: Job = dc.field(default_factory=Job)


@pdc
class Mlsm(AvroModel):
    class Meta:
        schema_doc = False

    lead_ranking: str = ""
    lead_rating: str = ""
    interest_level: str = ""
    qualification_level: str = ""
    all_scores: str = ""


@pdc
class LeadScore(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "mlsm": "Mlsm"
        }

    mlsm: Mlsm = dc.field(default_factory=Mlsm)


@pdc
class MarketingDescriptors(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "lead_score": "LeadScore"
        }

    persona: str = ""
    super_region: str = ""
    sub_region: str = ""
    penalty_box_reason: str = ""
    penalty_box_expiration: str = ""
    lead_score: LeadScore = dc.field(default_factory=LeadScore)


@pdc
class Privacy(AvroModel):
    class Meta:
        schema_doc = False

    consent_email_marketing: str = ""
    consent_email_marketing_timestamp: str = ""
    consent_email_marketing_source: str = ""
    consent_share_to_partner: str = ""
    consent_share_to_partner_timestamp: str = ""
    consent_share_to_partner_source: str = ""
    consent_phone_marketing: str = ""
    consent_phone_marketing_timestamp: str = ""
    consent_phone_marketing_source: str = ""


@pdc
class OptIn(AvroModel):
    class Meta:
        schema_doc = False

    f_formdata_optin: str = ""
    f_formdata_optin_phone: str = ""
    f_formdata_sharetopartner: str = ""


@pdc
class Location(AvroModel):
    class Meta:
        schema_doc = False

    city_from_ip: str = ""
    state_province_from_ip: str = ""
    postal_code_from_ip: str = ""
    country_from_ip: str = ""
    country_from_dns: str = ""


@pdc
class LastSubmission(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "opt_in": "OptIn",
            "location": "Location"
        }

    submission_date: str = ""
    submission_source: str = ""
    opt_in: OptIn = dc.field(default_factory=OptIn)
    location: Location = dc.field(default_factory=Location)



@pdc
class SfdcLeadId(AvroModel):
    class Meta:
        schema_doc = False

    lead_id: str = ""
    record_status: str = ""


@pdc
class SfdcContactId(AvroModel):
    class Meta:
        schema_doc = False

    contact_id: str = ""
    account_id: str = ""
    record_status: str = ""


@pdc
class Tombstone(AvroModel):
    class Meta:
        schema_doc = False

    is_tombstoned: str = ""
    tombstone_timestamp: str = ""
    tombstone_source: str = ""
    delete_all_data: str = ""


@pdc
class TrackingIds(AvroModel):
    class Meta:
        schema_doc = False
        alias_nested_items = {
            "sfdc_lead_id": "SfdcLeadId",
            "sfdc_contact_id": "SfdcContactId"
        }

    eloqua_contact_id: str = ""
    sfdc_lead_ids: typing.List[SfdcLeadId] = dc.field(default_factory=lambda: [SfdcLeadId().asdict()])
    sfdc_contact_ids: typing.List[SfdcContactId] = dc.field(default_factory=lambda: [SfdcContactId().asdict()])
