API_TITLE = "Change Event Service"
API_VERSION = "v1"
OPENAPI_VERSION = "3.0.2"
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_JSON_PATH = "/v3/api-docs"
OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.0.0-rc.4/"
ACTUATOR_BASE_URI = "http://localhost:5000/actuator"

SCHEDULER_API_ENABLED = True
SCHEDULER_ALLOWED_HOSTS = ["*"]

SQLALCHEMY_DATABASE_URI = "sqlite:///change_event_service.db"
SQLALCHEMY_TRACK_MODIFICATIONS = True
# SQLALCHEMY_ECHO = True

MQ_HOST = 'localhost'
MQ_VHOST = 'change_event_service'
MQ_QUEUE = 'change_event_service'
MQ_USER = 'guest'
MQ_PASSWORD = 'guest'
MQ_EXCHANGE = 'change_event_service'
MQ_ROUTING_KEY = 'change_event_service'
