import os
from django.contrib.messages import constants as messages
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from crequest.middleware import CrequestMiddleware

# -----------------------------------------------------------------------------
# REQUIRED VALUES
# -----------------------------------------------------------------------------
# Environment choices: {DEV, TEST, PROD}
ENVIRONMENT = 'DEV'

# Name of machine running the application
ALLOWED_HOSTS = ['localhost']

# Debug mode (probably only true in DEV)
DEBUG = True

# SSO URL
CAS_SERVER_URL = 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login'

# `````````````````
# FINTI
# `````````````````
# REQUIRED: Finti URL and Token (uncomment these):
FINTI_TOKEN = "2144402c-586e-44fc-bd0c-62b31e98394d"
FINTI_URL = 'https://ws-test.oit.pdx.edu'

# Finti URLs (for reference)
# -  http://localhost:8888
# -  http://127.0.0.1:5000
# -  https://ws-test.oit.pdx.edu
# -  https://ws.oit.pdx.edu

# As-of psu-base 0.11.0, Finti responses can be cached for offline development
FINTI_SAVE_RESPONSES = True    # Save/record actual Finti responses for offline use?
FINTI_SIMULATE_WHEN_POSSIBLE = False

DISABLE_GRAVATAR = True

# Email Settings
EMAIL_HOST_USER = 'cefr-app-mail'
EMAIL_HOST_PASSWORD = 'EuDFxamEfm7y'

# BI Data Export Settings
BI_EXPORT_ACCESS_KEY = 'AKIA5NHEHMJ35RRUG2EE'
BI_EXPORT_SECRET_KEY = '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'

# -----------------------------------------------------------------------------
# OPTIONAL VALUES
# -----------------------------------------------------------------------------

# You may want to disable elevated developer access while running locally
# ELEVATE_DEVELOPER_ACCESS = False

# You may want to extend session expiration during local development
# SESSION_COOKIE_AGE = 4 * 60 * 60  # 4 hours
# SESSION_COOKIE_AGE = 3.5 * 60  # 4 minutes


# Sentry log and performance monitoring
USE_SENTRY = False
if USE_SENTRY:
    # Prevent [POSTED] log messages from creating issues in Sentry
    # ----------------------------------------------------------------------
    def ignore_posted_messages(event, hint):
        ignore = logged_msg = browser = None

        # Get the log message that caused this event
        if 'log_record' in hint and hasattr(hint['log_record'], 'msg'):
            logged_msg = hint['log_record'].msg
        if (not logged_msg) and 'logentry' in event and 'message' in event['logentry']:
            logged_msg = event['logentry']['message']

        # Get the browser (was this an AWS health check?)
        if 'request' in event and 'headers' in event['request'] and 'User-Agent' in event['request']['headers']:
            browser = event['request']['headers']['User-Agent']
        is_health_check = browser and 'ELB-HealthChecker' in browser

        # Ignore POSTED errors (i.e. "You forgot to enter this required field...")
        ignore = logged_msg and ('[POSTED]' in logged_msg or '[DUPLICATE]' in logged_msg)

        return None if ignore else event

    # ----------------------------------------------------------------------
    # Limit performance sampling events
    # ----------------------------------------------------------------------
    def traces_sampler(sampling_context):
        exclusions = ['/psu/test', '/scheduler/run']
        default_rate = 0.1
        chosen_rate = default_rate
        try:
            if sampling_context["parent_sampled"] is not None:
                return sampling_context["parent_sampled"]

            path_info = sampling_context["wsgi_environ"].get('PATH_INFO') if "wsgi_environ" in sampling_context else None
            if path_info:
                # Note: This will only work if URL_CONTEXT is not defined (which it shouldn't be for AWS apps)
                chosen_rate = 0 if path_info in exclusions else default_rate
        except Exception as ee:
            print(f"Sampling context error: {ee}")
        print(f"SAMPLE RATE: {chosen_rate}")
        return chosen_rate


    # ----------------------------------------------------------------------

    # To which project should data be sent
    psu_base_dsn = 'https://dd64afb5b3f64bb392e315dc84c47e8c@o50547.ingest.sentry.io/5552755'
    sentry_env = f"local_dev"


    sentry_sdk.init(
        environment=sentry_env,
        dsn=psu_base_dsn,
        integrations=[DjangoIntegration()],
        traces_sampler=traces_sampler,
        traces_sample_rate=float(os.environ.get('SENTRY_SAMPLE_RATE', 1.0)),
        before_send=ignore_posted_messages,
        # If you wish to associate users to errors you may enable sending PII data.
        send_default_pii=str(os.environ.get('SENTRY_PII', 'True')).lower() == 'true'
    )
