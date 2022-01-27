from cloudcix.client import Client


class Vault:
    """
    The Vault application provides services that allow for interaction with MinIO object sorage for purposes such as
    storing files and sharing files with linked addresses.
    """
    _application_name = 'vault'
    bucket = Client(
        _application_name,
        '{region_name}/bucket/{path}/',
    )
    obj = Client(
        _application_name,
        '{region_name}/bucket/{path}/',
    )
    region = Client(
        _application_name,
        'region/',
    )
    share = Client(
        _application_name,
        'share/',
    )
    shared_bucket = Client(
        _application_name,
        '{region_name}/share/bucket/{path}/',
    )
    shared_object = Client(
        _application_name,
        '{region_name}/share/object/{path}/',
    )
