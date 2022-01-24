"""
The intention of this file is to gather all API error messages in a single easy-to-access place,
to allow us to re-use and unify a lot of our error messaging.

General styling:
---
For any error message that requires some kind of parameters, we will use a static method in a class

class SomeError:
    @staticmethod
    def complex_error_message(...) -> str:
        # build some_complex_string from parameters
        return some_complex_string

When importing these, it's recommended to import the class itself, and not just the function:

import DKCommon.constants.api.errors.SomeError
print(SomeError.complex_error_message(foo, bar, baz))

---

For all other error messages that are just strings, we just use a simple constant

SOME_ERROR = "This is a boring error message"

---

TODO:  WHEN THIS FILE GETS TOO LARGE, WE SHOULD SPLIT THIS UP INTO SEPARATE FILES FOR EACH `# region`
# Note:  the [region/endregion] comments are used by PyCharm for code collapsing.  It is recommended you use them!
"""

from typing import Union, Type, Any, Set, Optional


def object_type_as_str(object_type: Union[Type, str]) -> str:
    return (object_type if isinstance(object_type, str) else object_type.__name__).capitalize()


# region Shared
# Simple errors
NO_REQUEST_BODY_ALLOWED = "This endpoint does not support a request body"


# Complex errors
class SharedErrors:
    @staticmethod
    def not_found(object_type: Union[Type, str], object_id: Union[int, str]) -> str:
        return f"Could not find {object_type_as_str(object_type)} with ID '{object_id}'"

    @staticmethod
    def not_found_inside(
        object_type: Union[Type, str],
        object_id: Union[int, str],
        outer_obj_type: Union[Type, str],
        outer_obj_id: Union[int, str],
    ) -> str:
        return f"{SharedErrors.not_found(object_type, object_id)} within {object_type_as_str(outer_obj_type)} with ID '{outer_obj_id}'"

    @staticmethod
    def cannot_delete(object_type: Union[Type, str], object_id: Union[int, str]) -> str:
        return f"Error deleting {object_type_as_str(object_type)} with ID '{object_id}'"

    @staticmethod
    def incomplete_request_body(expected: str) -> str:
        return f"The request body is incomplete. expected: {expected}"


# endregion


# region DKResources
# Simple errors
BODY_SCHEMA_FAILED = "Schema check failed, request body is malformed"
NO_VALID_REQUEST_BODY_FOUND = "The request does not contain a valid JSON body"
INVALID_CONTENT_TYPE = "Invalid content-type. The content-type must indicate a JSON"
NO_FLASK_RESPONSE = "Expected a Flask 'Response' to be returned for the resource"
REQUEST_BODY_NOT_JSON = "The request body was malformed, check to make sure it is valid JSON"
BAD_AUTH_HEADER = "Malformed authentication header"
SCHEMA_NO_ADDITIONAL_PROPS = "The endpoint has an invalid schema: 'additionalProperties' must be False"
BAD_RESPONSE_BODY = "Invalid response body"


# Complex errors
class APIErrors:
    @staticmethod
    def exception_no_error_msg(exception_name: str) -> str:
        return f"{exception_name} did not provide an error message"

    @staticmethod
    def bad_status_code(status_code: Any) -> str:
        return f"Invalid Status Code: {status_code}"

    @staticmethod
    def endpoint_missing_permission(method: str) -> str:
        return f"A '{method}' endpoint is missing permissions"

    @staticmethod
    def cannot_reactivate_entity(entity: str) -> str:
        return f"You do not have the required permissions to reactivate this {entity}"


# endregion


# region System
# Simple errors
MISSING_ICON_NAME = "You must provide a valid, non-empty icon name"
MISSING_ICON_FILE = "You must provide an image file"
BAD_EMAIL_CREDENTIALS = "We were unable to send the email, ask the system administrator to check credentials"
EMAIL_NOT_SENT = "We were unable to send the email to support at this time, please try again later"
BAD_EMAIL_REQUEST_TYPE = "Invalid email request type"


# Complex errors
class SystemEndpointErrors:
    @staticmethod
    def invalid_file_extension(extension: str, allowed: Set[str]) -> str:
        return f"Invalid file extension '{extension}', must be one of {allowed}"

    @staticmethod
    def icon_exists(name: str) -> str:
        return f"An icon with the name '{name}' already exists"

    @staticmethod
    def icon_not_found(name: str) -> str:
        return f"An icon named '{name}' could not be found"

    @staticmethod
    def user_email_not_found(email: str) -> str:
        return f"No User exists with the email '{email}'"


# endregion


# region Auth
# Simple errors
BAD_CREDENTIALS = "Invalid credentials"
EXPIRED_REQUEST_ID = "This request is not valid or has expired"
SSO_NOT_SUPPORTED = "SSO is not supported for this customer"


# Complex errors
class AuthEndpointErrors:
    @staticmethod
    def bad_sso_user_data(field: str) -> str:
        return f"SSO User info is missing necessary field '{field}'"

    @staticmethod
    def sso_auth_failed(inner_error: Optional[str] = None) -> str:
        base_error = "SSO authentication has failed"
        if inner_error:
            return f"{base_error}:  [{inner_error}]"
        return base_error

    @staticmethod
    def oauth_error(inner_error: str) -> str:
        return f"Auth Provider error:  {inner_error}"


# endregion


# region User
# Simple errors
BAD_USER_DATA = "Unable to create a User with this information, please consult the API docs"
CANNOT_MAKE_ADMIN_NO_PERMISSION = "You must be an administrator to enable the administrator status"
CANNOT_MAKE_ADMIN_INELIGIBLE = "The target user is ineligible for the administrator status"
CANNOT_MAKE_SELF_ADMIN = "Admin Users cannot update their own administrative status"
BULK_PRIMARY_COMPANY_NOT_SET = "All Users must have 'primary_company_id' set (int)"
BULK_EMAIL_NOT_SET = "All User must have 'email' set (str)"


# Complex errors
class UserEndpointErrors:
    @staticmethod
    def bulk_user_bad_company(company_id: int, email: str) -> str:
        return f"Invalid Company ID '{company_id}' for {email}"


# endregion


# region Role
# Simple errors
USER_ASSIGN_BAD_IDS = "One or more of the User IDs supplied are invalid"
ONLY_SYSTEM_ROLES_FOR_COMPANY = "Cannot assign Users to non-System Roles for a Company"


# Complex errors
class RoleEndpointErrors:
    @staticmethod
    def bad_permission_name(name: str) -> str:
        return f"'{name}' is not a valid Permission"

    @staticmethod
    def user_needs_permission_on_parent(entity_name: str, entity_id: int) -> str:
        return f"Users must have a Role on the parent {entity_name} '{entity_id}'"


# endregion


# region Company
# Simple errors
INVALID_AUTH_PROVIDER_CONFIG = (
    "'auth_provider' has an invalid format, expected something like {'type': 'auth0', 'config': {...}}"
)
AUTH_PROVIDER_CREATE_UNKNOWN_FAILURE = "Something went wrong attempting to create the new auth provider"
CANNOT_MODIFY_COMPANY_CODE = "You are not permitted to modify the 'company_code' of a Company"
CANNOT_DEACTIVATE_DATAKITCHEN = "You are not allowed to deactivate the DataKitchen company"
INVALID_AUTH_PROVIDER_ID = "'auth_provider_id' must be a valid integer"


# Complex errors
class CompanyEndpointErrors:
    @staticmethod
    def cannot_delete_company_with_users(company_id: int) -> str:
        return f"Company '{company_id}' still has Users associated with it"

    @staticmethod
    def bad_auth_provider_type(auth_type: str) -> str:
        return f"Unknown authentication provider: {auth_type}"


# endregion
