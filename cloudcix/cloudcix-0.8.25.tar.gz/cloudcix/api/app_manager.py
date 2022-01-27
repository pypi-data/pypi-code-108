from cloudcix.client import Client


class AppManager:
    """
    The App Manager Application is a software system that manages CloudCIX Apps

    It allows Users to select and use apps, and allows Administrators to select which apps to deploy and give
    permissions to other Users.
    """
    _application_name = 'appmanager'

    app = Client(
        _application_name,
        'app/',
    )
    app_member = Client(
        _application_name,
        'app/{app_id}/member/',
    )
    app_menu = Client(
        _application_name,
        'app/{app_id}/menu_item/',
    )
    menu_item_user = Client(
        _application_name,
        'menu_item/user/{user_id}/',
    )
