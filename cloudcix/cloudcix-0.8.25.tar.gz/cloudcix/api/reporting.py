from cloudcix.client import Client


class Reporting:
    """
    The Reporting Engine is a powerful service allowing users to generate HTML and PDF documents from templates
    """
    _application_name = 'Reporting'

    export = Client(
        _application_name,
        'Export/',
    )
    package = Client(
        _application_name,
        'Package/',
    )
    report = Client(
        _application_name,
        'Report/',
    )
    report_template = Client(
        _application_name,
        'ReportTemplate/',
    )
