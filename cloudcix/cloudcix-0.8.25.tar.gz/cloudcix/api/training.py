from cloudcix.client import Client


class Training:
    """
    The Training Application exposes a REST API capable of managing Training records
    """
    _application_name = 'training'
    cls = Client(
        _application_name,
        'class/',
    )
    student = Client(
        _application_name,
        'student/',
    )
    syllabus = Client(
        _application_name,
        'syllabus/',
    )
