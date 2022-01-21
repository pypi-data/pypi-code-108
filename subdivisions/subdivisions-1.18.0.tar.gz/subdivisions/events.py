"""PubSub Events.

Declare here all PubSub topics which will be used.

These Topics will be created on AWS, when you send his first message.

"""
from enum import Enum


class UserEvents(Enum):
    USER_REGISTERED = "user_registered"
    USER_ACTIVATED = "user_activated"
    USER_LOGGED_IN = "user_logged_in"


class AccountEvents(Enum):
    BANK_ACCOUNT_REGISTERED = "bank_account_registered"
    AD_ACCOUNT_REGISTERED = "google_ad_account_registered"
    POLISHED_STATEMENT_TABLE = "polished_statement_table"
    STATEMENT_TABLE_UPDATED = "statement_table_updated"


class ProposalEvents(Enum):
    PROPOSAL_SELECTED = "proposal_selected"
    PROPOSAL_APPROVED = "proposal_approved"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_INDICATIVE = "proposal_indicative"
    PROPOSAL_REFUSED = "proposal_refused"
    PROPOSAL_EXPIRED = "proposal_expired"
    PROPOSAL_STATUS_UPDATED = "prpposal_status_updated"


class CompanyEvents(Enum):
    COMPANY_REGISTERED = "company_registered"
    COMPANY_UPDATED = "company_updated"


class HubspotEvents(Enum):
    ORIGINATION_REGISTERED = "origination_registered"
    ORIGINATION = "origination"
    ADDITIONAL_DATA_SENT = "additional_data_sent"
    LEAD_SCORE = "lead_score"


class AdsEvents(Enum):
    ADS_ACCOUNT_CONNECTION = "ads_account_connection"


class CredentialEvents(Enum):
    NEW_TAX_ID_REGISTERED = "new_tax_id_registered"


class PartnerEvents(Enum):
    I_WANT_TO_BE_A_PARTNER = "i_want_to_be_a_partner"


class PartnershipEvents(Enum):
    ORDER_NEW = "order_new"
    ORDER_DENIED = "order_denied"
    ORDER_APPROVED = "order_approved"
    ORDER_INDICATIVE = "order_indicative"
    ORDER_USER_VERIFICATION = "order_user_verification"


class ClientManagerEvents(Enum):
    SHAREHOLDER_REGISTRATION = "shareholder_registration"
    GUARANTOR_REGISTRATION = "guarantor_registration"
    PROCURATOR_REGISTER = "procurator_register"
    EXECUTIVE_REGISTRATION = "executive_registration"
    PEP_FORM = "pep_form"


class DocumentationEvents(Enum):
    GENERATED_DOCUMENTATION = "generated_documentation"
    DOCUMENTATION_OK = "documentation_ok"
    DISBURSEMENT_MADE = "disbursement_made"
    CLIENT_PROCESS_APPROVED = "client_process_approved"
    CLIENT_PROCESS_WITH_PENDENCIES = "client_process_with_pendencies"


class AssetEvents(Enum):
    CREATED_EXPECTED_CASHFLOW_ENTRY = "created_expected_cashflow_entry"
    CREATED_INSTRUMENT = "created_instrument"


class BankEvents(Enum):
    CREATED_BOLETO = "created_boleto"
    UPDATED_BOLETO = "updated_boleto"
    CREATED_BOLETO_PROCESSED = "created_boleto_processed"
