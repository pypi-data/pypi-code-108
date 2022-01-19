from psu_base.services import message_service, utility_service, error_service
from psu_base.classes.Log import Log
from functools import wraps
from urllib.parse import urlparse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url
from psu_base.services import auth_service
from datetime import datetime

log = Log()


# ===                                ===
# === AUTHENTICATION & AUTHORIZATION ===
# ===                                ===


def require_authority(authority_code, redirect_url="/"):
    """
    Decorator for views that checks that the user has the required authority.

    authority_code: An authority_code, or a list of authority codes
    redirect_url: Where to send unauthorized user

    Example:
        from psu_base.decorators import require_authority

        # This will redirect unauthorized users to the status test page.
        # If no redirect_url is specified, the root url will be used ("/")
        @require_authority('fake', redirect_url='psu:test')
        def index(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # If has authority, render the view
            elif auth_service.has_authority(authority_code):
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                if utility_service.get_flash_variable("new_impersonation"):
                    log.info(
                        "Impersonated user does not have access to last page. Redirecting..."
                    )
                else:
                    message_service.post_error(
                        "You are not authorized to perform the requested action"
                    )
                return decorator_redirect(request, redirect_url)

        return _wrapped_view

    return decorator


def require_authentication():
    """
    Decorator for views that forces them to log in.

    Example:
        from psu_base.decorators import require_authentication

        @require_authentication()
        def index(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # Otherwise, render the view
            else:
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_impersonation_authority(redirect_url="/"):
    """
    Decorator for views that forces them to have access to impersonate someone else.

    Example:
        from psu_base.decorators import require_impersonation_authority

        @require_impersonation_authority()
        def index(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If not logged in, redirect to login
            if not request.user.is_authenticated:
                return decorator_sso_redirect(request)

            # If has authority, render the view
            elif auth_service.get_auth_object().can_impersonate():
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                message_service.post_error(
                    "You are not authorized to impersonate other users."
                )
                return decorator_redirect(request, redirect_url)

        return _wrapped_view

    return decorator


# ===                 ===
# === FEATURE TOGGLES ===
# ===                 ===


def require_feature(feature_code, redirect_url="/"):
    """
    Decorator for views that forces specified feature to be enabled.

    Example:
        from psu_base.decorators import require_feature

        @require_feature('admin_script')
        def index(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If feature is active, render the view
            if utility_service.feature_is_enabled(feature_code):
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                message_service.post_error(
                    "The requested feature is currently disabled."
                )
                return decorator_redirect(request, redirect_url)

        return _wrapped_view

    return decorator


def feature_redirect(feature_code, redirect_url="/"):
    """
    Decorator for views that redirects to specified URL if feature is active.
    (this is essentially the opposite of @require_feature)

    Example:
        from psu_base.decorators import feature_redirect

        @feature_redirect('fye_downtime', 'my_app:fye_downtime')
        def index(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If feature is active, redirect to specified feature URL
            if utility_service.feature_is_enabled(feature_code):
                return decorator_redirect(request, redirect_url)

            # Otherwise, render the view
            else:
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# ===                 ===
# ===      MISC.      ===
# ===                 ===


def require_non_production(redirect_url="/"):
    """
    Decorator for views that limits it to non-production use only

    Example:
        from psu_base.decorators import require_non_production

        @require_non_production()
        def test_page(request):
            pass
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):

            # If in non-production, render the view
            if utility_service.is_non_production():
                return view_func(request, *args, **kwargs)

            # Otherwise, send somewhere else
            else:
                message_service.post_error(
                    "The requested page is only available in non-production environments."
                )
                return decorator_redirect(request, redirect_url)

        return _wrapped_view

    return decorator


def trace(metrics=False, log_result=False):
    """
    Trace function (including parameters) and optionally log the result
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_func(*args, **kwargs):
            module = func.__module__
            if "." in module:
                p = module.split(".")
                module = p[len(p) - 1]
                del p

            function_name = f"{module}.{func.__name__}"

            params = ", ".join([str(x)[:20] for x in args]) if args else ""
            if kwargs:
                for kk, vv in kwargs.items():
                    params += f"{kk}={str(vv)[:20]}, "
            params = params.strip(", ")

            log.debug(f"TRACE : {function_name}({params})")

            # Run the function
            result = had_error = None
            start_time = datetime.now()
            result = func(*args, **kwargs)

            end_time = datetime.now()
            delta = end_time - start_time
            duration = str(int(delta.total_seconds() * 1000))
            metric_txt_add_on = f"-- completed in {duration} ms"

            if log_result:
                log.debug(f"RETURN: {function_name} -> {result} {metric_txt_add_on}")
            elif metrics:
                log.debug(f"RETURN: {function_name} {metric_txt_add_on}")

            return result

        return _wrapped_func

    return decorator


#
# REMAINING GENERIC CODE IS CALLED FROM THE DECORATORS ABOVE
#


def decorator_redirect(request, redirect_url):
    # Do not redirect on AJAX requests, just return as failure
    if utility_service.is_ajax():
        return HttpResponseForbidden()

    resolved_login_url = resolve_url(redirect_url)
    path = request.build_absolute_uri()
    from django.contrib.auth.views import redirect_to_login

    return redirect_to_login(path, resolved_login_url, None)


def decorator_sso_redirect(request):
    resolved_login_url = resolve_url("cas:login")
    path = request.build_absolute_uri()
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if (not login_scheme or login_scheme == current_scheme) and (
        not login_netloc or login_netloc == current_netloc
    ):
        path = request.get_full_path()
    from django.contrib.auth.views import redirect_to_login

    return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)
