from cloudcix.client import Client


class Contacts:
    """
    The Contacts Application is a CRM application that exposes a REST API to manage a shared address book between Users
    in the same Member

    Contacts can be used as a sales and marketing tool or just as a general purpose address book.
    """
    _application_name = 'Contacts'

    activity = Client(
        _application_name,
        'ActivityType/{activity_type_id}/Activity/',
    )
    activity_type = Client(
        _application_name,
        'ActivityType/',
    )
    campaign = Client(
        _application_name,
        'Campaign/',
    )
    campaign_activity = Client(
        _application_name,
        'Campaign/{campaign_id}/Activity/',
    )
    campaign_contact = Client(
        _application_name,
        'Campaign/{campaign_id}/Contact/',
    )
    contact = Client(
        _application_name,
        'Contact/',
    )
    group = Client(
        _application_name,
        'Group/',
    )
    group_contact = Client(
        _application_name,
        'Group/{group_id}/Contact/',
    )
    opportunity = Client(
        _application_name,
        'Opportunity/',
    )
    opportunity_contact = Client(
        _application_name,
        'Opportunity/{opportunity_id}/Contact/',
    )
    opportunity_history = Client(
        _application_name,
        'Opportunity/{opportunity_id}/History/',
    )
