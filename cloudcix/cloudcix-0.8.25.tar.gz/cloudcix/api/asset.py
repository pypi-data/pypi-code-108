from cloudcix.client import Client


class Asset:
    """
    The Asset Application enables the management of Assets owned by a Member.

    Examples of Assets are buildings, machinery, furniture, vehicles, etc.
    """
    _application_name = 'Asset'

    asset = Client(
        _application_name,
        'Asset/',
    )
    asset_transaction = Client(
        _application_name,
        'Asset/{asset_id}/Transaction/',
    )
    depreciation_type = Client(
        _application_name,
        'DepreciationType/',
    )
    off_rent = Client(
        _application_name,
        'OffRent/',
    )
    off_test = Client(
        _application_name,
        'OffTest/',
    )
    rent = Client(
        _application_name,
        'Rent/',
    )
