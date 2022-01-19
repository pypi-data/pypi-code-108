from psu_base.services import utility_service
from psu_base.classes.IdentityCAS import IdentityCAS
from psu_base.classes.Log import Log
from psu_base.classes.Auth import Auth
from psu_base.models.audit import Audit
from psu_base.models.student import Student
from psu_base.classes.DynamicRole import DynamicRole
from django.contrib.auth.models import User
from psu_base.classes.User import User as PSUser
from psu_base.classes.Finti import Finti

log = Log()


def get_auth_object():
    return Auth(auto_resume=True)


def get_user():
    return get_auth_object().get_user()


def get_student(user_instance=None):
    """Get student identity as a Django model (psu_base.models.Student)"""
    if not user_instance:
        user_instance = get_user()
    if user_instance and user_instance.psu_id:
        student = Student.get_by_psu_id(user_instance.psu_id)
        if not student:
            try:
                student = Student()
                student.username = user_instance.username
                student.psu_id = user_instance.psu_id
                student.pidm = user_instance.pidm
                student.email_address = user_instance.email_address
                student.first_name = user_instance.first_name
                student.last_name = user_instance.last_name
                student.save()
            except Exception as ee:
                log.error(f"Unable to create student: {ee}")
                student = None
        if student:
            return student
    return None


def is_logged_in():
    return get_auth_object().is_logged_in()


def has_authority(authority_code, sso_user_only=False, require_global=False):
    return get_auth_object().has_authority(
        authority_code, sso_user_only=sso_user_only, require_global=require_global
    )


def get_authorized_users(authority_code):
    """
    Get all users that have the specified authority (or authorities)
    """
    log.trace()

    # If single authority was given, turn it into a list
    if authority_code and type(authority_code) is not list:
        if "," in authority_code:
            authority_list = utility_service.csv_to_list(authority_code)
        else:
            authority_list = [authority_code]
    elif authority_code:
        authority_list = authority_code
    else:
        return []

    # Expand dynamic roles
    clean_authorities = []
    for code in authority_list:
        if code.startswith("~") or code.upper().startswith("DYNAMIC"):
            clean_authorities.extend(DynamicRole().decode(code))
        else:
            clean_authorities.append(code)
    authority_list = clean_authorities
    del clean_authorities

    # Get all permissions for the current app (includes global)
    permissions = Finti().get(
        f"wdt/v1/sso_proxy/manage/permissions/{utility_service.get_app_code()}"
    )
    if type(permissions) is not list:
        permissions = []

    # Group users by authority code { auth_code: [usernames], ... }
    permission_dict = {}
    for pp in permissions:
        authority_code = pp["authority_code"]
        if authority_code not in authority_list:
            # Ignore authorities that were not specified
            continue
        if authority_code not in permission_dict:
            permission_dict[authority_code] = []
        permission_dict[authority_code].append(pp["username"])
    del permissions

    # Gather usernames that have specified authorities
    authorized_usernames = []
    for authority_code in authority_list:
        if authority_code in permission_dict:
            authorized_usernames.extend(permission_dict[authority_code])
    authorized_usernames = list(set(authorized_usernames))
    del permission_dict
    del authority_list

    # Get user objects from usernames
    authorized_users = [look_up_user_cache(un) for un in authorized_usernames]
    del authorized_usernames

    num_authorized = len(authorized_users)
    if num_authorized == 0:
        log.end("No authorized users")
    elif num_authorized > 20:
        log.end(f"{num_authorized} authorized users")
    else:
        log.end(authorized_users)
    return authorized_users


def audit_event(
    event_code,
    previous_value=None,
    new_value=None,
    comments=None,
    reference_code=None,
    reference_id=None,
):
    """Audit some important event performed by an authenticated user"""
    log.trace()

    # Replace "new-line" strings with new-line character
    if comments and "\\n" in comments:
        comments = comments.replace("\\n", "\n")

    auth = get_auth_object()
    audit_instance = Audit(
        app_code=utility_service.get_app_code(),
        username=auth.sso_user.username,
        event_code=event_code,
        previous_value=str(previous_value)[:500] if previous_value else previous_value,
        new_value=str(new_value)[:500] if new_value else new_value,
        comments=comments,
        reference_code=str(reference_code)[:60] if reference_code else reference_code,
        reference_id=reference_id,
    )

    # If the user is impersonating or proxying, show the proxied user
    # This may help track down how something changed for a user that did not actually perform the event
    if auth.is_impersonating():
        audit_instance.impersonated_username = auth.impersonated_user.username
    if auth.proxied_user and auth.proxied_user.is_valid():
        audit_instance.proxied_username = auth.proxied_user.username

    # Save the audit record
    audit_instance.save()


def look_up_user_cache(user_info):
    """
    Look up a person's Identity (not including authorities), and retain it for
    the duration of the request to allow repeat lookups without hitting Finti each time
    """
    user_info = str(user_info)
    user_map = _cached_users(user_info)
    if user_info in user_map:
        return user_map[user_info]
    else:
        return None


#
# REMAINING CODE IS CALLED AUTOMATICALLY. YOU SHOULDN'T CALL IT ANY OTHER WAY.
#


def set_sso_user(request):
    """Save the SSO-authenticated user into the session, or remove it if logged out"""
    auth = Auth(auto_resume=True)

    # If logged in
    if request.user.is_authenticated:
        # Put CAS attributes into more intuitively named (and auto-completable) properties
        cas_id = IdentityCAS(request)

        # Was this user already logged in?
        returning_user = auth.is_logged_in() and cas_id.equals(auth.sso_user.username)

        # If using sub-apps, did the sub-app change?
        sub_app_info = utility_service.get_sub_app_info()
        app_changed = sub_app_info and sub_app_info.get("app_changed")
        is_sub_app = sub_app_info and sub_app_info.get("is_sub_app")

        # If this user is already saved, no need to update it unless the sub-app just changed
        if not returning_user:
            log.trace()  # Only trace this on initial login
            utility_service.set_session_var("psu_base_sso_username", cas_id.username)

            # Create a new Auth object. Includes identity and authorities
            auth = Auth(cas_id.username)

            # Update Django staff/superuser permissions for access to admin pages
            # Only do this for the primary app, not sub-apps
            if not is_sub_app:
                try:
                    django_user = User.objects.get(username=cas_id.username)
                    if auth.has_authority("~SuperUser"):
                        if not django_user.is_staff:
                            django_user.is_staff = 1
                            django_user.is_superuser = 1
                            django_user.save()
                    else:
                        if django_user.is_staff:
                            django_user.is_staff = 0
                            django_user.is_superuser = 0
                            django_user.save()
                except Exception as ee:
                    log.error("Unable to update Django user permissions")

        # If returning user is in a new sub-app, permissions need to be refreshed
        elif app_changed:
            # Refresh each user object
            auth.sso_user = PSUser(auth.sso_user.username)
            if auth.is_impersonating():
                auth.impersonated_user = PSUser(auth.impersonated_user.username)
            if auth.is_proxying():
                auth.proxied_user = PSUser(auth.proxied_user.username)

    # If not logged in
    else:
        utility_service.set_session_var("psu_base_sso_username", None)

    auth.save()

    # Features may be Limited to administrators during testing/validation of new features
    # To avoid circular imports when checking for admin authority from utility_service, flag admins
    # in the temp session. This should remain true even while impersonating non-admins (for limited features only).
    utility_service.set_session_var(
        "allow_limited_features", True if has_authority("~PowerUser") else None
    )


def _cached_users(user_info):
    user_map = utility_service.recall()
    if user_map and user_info in user_map:
        return user_map
    else:
        if type(user_map) is not dict:
            user_map = {}

        user_instance = PSUser(user_info, get_authorities=False)
        if user_instance:
            user_map[user_info] = user_instance

    return utility_service.store(user_map)
