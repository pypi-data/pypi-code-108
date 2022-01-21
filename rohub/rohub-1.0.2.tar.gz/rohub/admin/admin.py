from rohub import settings
from rohub import utils
from rohub import rohub


def validate_authentication_token(func):
    def func_wrapper(*args, **kwargs):
        if utils.is_valid(token_type="access"):
            valid_token = True
        else:
            valid_token = utils.refresh_access_token()
        if valid_token:
            return func(*args, **kwargs)
    return func_wrapper


@validate_authentication_token
def delete_external_user(user_identifier):
    """
    Function that deletes specific external user.

    .. warning::
        The operation is permitted only if you are logged into account with admin privileges

    :param user_identifier: user's identifier
    :type user_identifier: str
    :returns: response/None
    :rtype: dict/None
    """
    profile_details = rohub.show_my_user_profile_details()
    roles = profile_details.get("roles", "unknown")   # if for some reason we could not find roles, set it to unknown
    if "admin" not in roles:
        print("Account you are currently logged in doesn't have admin permissions!")
        print("Therefore, you are not allowed to execute this action!")
        return
    url = settings.API_URL + f"external_users/{user_identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("User successfully deleted!")
        return


@validate_authentication_token
def delete_organization(organization_identifier):
    """
    Function that deletes specific organization.

    .. warning::
        The operation is permitted only if you are logged into account with admin privileges

    :param organization_identifier: user's identifier
    :type organization_identifier: str
    :returns: response/None
    :rtype: dict/None
    """
    profile_details = rohub.show_my_user_profile_details()
    roles = profile_details.get("roles", "unknown")   # if for some reason we could not find roles, set it to unknown
    if "admin" not in roles:
        print("Account you are currently logged in doesn't have admin permissions!")
        print("Therefore, you are not allowed to execute this action!")
        return
    url = settings.API_URL + f"organizations/{organization_identifier}/"
    r = utils.delete_request(url=url)
    if r.status_code != 204:
        content = r.json()
        return content
    else:
        print("Organization successfully deleted!")
        return
