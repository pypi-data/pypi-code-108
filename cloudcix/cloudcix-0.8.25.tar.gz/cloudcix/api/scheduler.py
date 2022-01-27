from cloudcix.client import Client


class Scheduler:
    """
    Scheduler is an application that allows the User to create recurring transactions.

    A recurring transaction is a transaction that will be recreated one or several times according to the rules the
    User gives.
    """
    _application_name = 'scheduler'

    task = Client(
        application=_application_name,
        service_uri='task/',
    )
    task_log = Client(
        application=_application_name,
        service_uri='task_log/',
    )
