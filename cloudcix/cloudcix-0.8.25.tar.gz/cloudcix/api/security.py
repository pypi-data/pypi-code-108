from cloudcix.client import Client


class Security:
    """
    Security is a service whose main function is to manage visitors and staff entering and exiting a building.

    Users will be able to see where they went and when.

    Administrators will be able to see where their Users went and when, as well as visitors to their own Addresses
    """
    _application_name = 'Security'

    security_event = Client(
        _application_name,
        'SecurityEvent/',
    )
    security_event_logout = Client(
        _application_name,
        'SecurityEvent/{user_id}/Logout/',
    )
