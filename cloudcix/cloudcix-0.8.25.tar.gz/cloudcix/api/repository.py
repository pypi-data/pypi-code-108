from cloudcix.client import Client


class Repository:
    """
    The Repository Application is a software system that manages CloudCIX Software Projects

    Projects in the Repository are grouped by the owning Member
    """
    _application_name = 'SupportFramework'

    application = Client(
        _application_name,
        'Member/{member_id}/Application/',
    )
    dto = Client(
        _application_name,
        'DTO/',
    )
    dto_parameter = Client(
        _application_name,
        'DTO/{dto_id}/Parameter/',
    )
    exception_code = Client(
        _application_name,
        'ExceptionCode/',
    )
    language_exception_code = Client(
        _application_name,
        'ExceptionCode/{exception_code}/Language/',
    )
    member = Client(
        _application_name,
        'Member/',
    )
    method = Client(
        _application_name,
        'Member/{member_id}/Application/{application_id}/Service/{service_id}/Method/',
    )
    method_parameter = Client(
        _application_name,
        'Member/{member_id}/Application/{application_id}/Service/{service_id}/Method/{method_id}/Parameter/',
    )
    service = Client(
        _application_name,
        'Member/{member_id}/Application/{application_id}/Service/',
    )
