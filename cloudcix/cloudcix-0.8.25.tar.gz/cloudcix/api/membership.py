from cloudcix.client import Client


class Membership:
    """
    Membership is a CloudCIX Application that exposes a REST API capable of managing CloudCIX Members and relationships
    between those Members
    """
    _application_name = 'membership'
    address = Client(
        _application_name,
        'address/',
    )
    address_link = Client(
        _application_name,
        'address/{address_id}/link/',
    )
    cloud_bill = Client(
        _application_name,
        'cloud_bill/{address_id}/{target_address_id}/',
    )
    country = Client(
        _application_name,
        'country/',
    )
    currency = Client(
        _application_name,
        'currency/',
    )
    department = Client(
        _application_name,
        'department/',
    )
    email_confirmation = Client(
        _application_name,
        'email_confirmation/{email_token}',
    )
    language = Client(
        _application_name,
        'language/',
    )
    member = Client(
        _application_name,
        'member/',
    )
    member_link = Client(
        _application_name,
        'member/{member_id}/link/',
    )
    notification = Client(
        _application_name,
        'address/{address_id}/notification/',
    )
    profile = Client(
        _application_name,
        'profile/',
    )
    subdivision = Client(
        _application_name,
        'country/{country_id}/subdivision/',
    )
    team = Client(
        _application_name,
        'team/',
    )
    territory = Client(
        _application_name,
        'territory/',
    )
    token = Client(
        _application_name,
        'auth/login/',
    )
    transaction_type = Client(
        _application_name,
        'transaction_type/',
    )
    user = Client(
        _application_name,
        'user/',
    )
    verbose_address = Client(
        _application_name,
        'address/verbose/',
    )
