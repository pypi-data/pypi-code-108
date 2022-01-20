"""Share Constants"""

# ******* Consts *******
DEFAULT_APPID = "default"
DEFAULT_PUBSUB_NAME = "pubsub"

# ******* Env Names *******
ENV_NAME_SERVICE_RUN_MODE = 'SERVICE_RUN_MODE'
ENV_NAME_DAPR_APP_ID = 'APP_ID'

# ******* Route Tag Names *******
ROUTE_TAG_NAME_AUTO_REGISTER = 'Auto Register'

# ******* Share Event Topic Names *******
EVENT_TOPIC_NAME_SERVICE_REGISTER = 'service_register'
EVENT_TOPIC_NAME_SCHEDULE_TASK_REGISTER = 'schedule_task_register'

# ******* Share Event Subscribe Route Names *******
EVENT_SUBSCRIBE_ROUTE_SERVICE_REGISTER = 'subscribe_service_register'
EVENT_SUBSCRIBE_ROUTE_SCHEDULE_TASK_REGISTER = 'subscribe_schedule_task_register'

# ******* Service Share Invoke Route Names *******
INVOKE_ROUTE_POLICY_SERVICE_SCHEDULE_TASK_REGISTER = 'v1/manage/register/service'

# ******* Content Types *******
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_TEXT = 'text/plain'

# ******* HTTP Verbs *******
HTTP_VERB_GET = 'GET'
HTTP_VERB_POST = 'POST'
HTTP_VERB_DELETE = 'DELETE'
HTTP_VERB_PUT = 'PUT'
HTTP_VERB_PATCH = 'PATCH'
HTTP_VERB_OPTION = 'OPTION'
HTTP_VERB_HEAD = 'HEAD'

# ******* Service Names *******
SERVICE_NAME_POLICY = 'policy'
