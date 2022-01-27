from cloudcix.client import Client


class Circuit:
    """
    The Circuit Application allows for the management of circuits and devices.
    """
    _application_name = 'Circuit'

    circuit = Client(
        _application_name,
        'Circuit/',
    )
    circuit_class = Client(
        _application_name,
        'CircuitClass/',
    )
    property_type = Client(
        _application_name,
        'PropertyType/',
    )
