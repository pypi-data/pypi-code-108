import os

class Config(object):
  """
  Parent configuration class.

  Add all config attributes in the parent class with a default.
  Then override as needed in the environment specific configs
  """
  LOG_APP_NAME= os.getenv('LOG_APP_NAME')
  LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
  GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
  PC_MILER_URL = "https://pcmiler.alk.com/apis/rest/v1.0/Service.svc/locations?postcodeFilter={0}&dataset=Current&authToken={1}"
  PC_MILER_KEY = os.getenv('PC_MILER_KEY')
  LOCATION_REDIS_URL = os.getenv('LOCATION_REDIS_URL')
  LOCATION_REDIS_PWD = os.getenv('LOCATION_REDIS_PWD')
  DISTANCE_CACHE_URL = os.getenv('DISTANCE_CACHE_URL')
  DISTANCE_CACHE_PASSWORD = os.getenv('DISTANCE_CACHE_PASSWORD')
  TIMEZONE_CACHE_URL = os.getenv('TIMEZONE_CACHE_URL')
  TIMEZONE_CACHE_PASSWORD = os.getenv('TIMEZONE_CACHE_PASSWORD')
  PC_MILER_HOURLY_LIMIT = 14000
  PC_MILER_MONTHLY_LIMIT = 300000
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-parsed-carrier-test'
  PARSED_CARRIER_SNS_SUBJECT = 'parsed-carrier'
  PARSED_CARRIER_SNS_CLASS_NAME = 'com.cargochief.sdk.carrierhub.notifications.ParsedCarrierNotification'
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-book-load-test'
  BOOK_LOAD_SNS_SUBJECT = 'book-load'
  BOOK_LOAD_SNS_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.BookLoadNotification'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-assistant-flow-test'
  BOOKING_ASSISTANT_SNS_SUBJECT = 'booking-assistant-flow'
  BOOKING_ASSISTANT_SNS_CLASS_NAME = 'com.cargochief.sdk.bookingagent.sns.BookingAssistantFlowNotification'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-movements-test'
  IMPORT_MOVEMENTS_SNS_SUBJECT = 'import-movements'
  IMPORT_MOVEMENTS_SNS_CLASS_NAME = 'com.cargochief.sdk.c4.sns.mcleod.ImportMovementsNotification'
  IMPORT_CARRIERS_SNS_SUBJECT = 'import-carriers'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-carriers-test'

class LocalConfig(Config):
  """Configurations for running and debugging locally, with a separate local database."""
  LOCATION_REDIS_URL='redis://localhost:6379'
  LOCATION_REDIS_PWD=None
  DISTANCE_CACHE_URL='redis://localhost:6379'
  DISTANCE_CACHE_PASSWORD=None
  TIMEZONE_CACHE_URL='redis://localhost:6379'
  TIMEZONE_CACHE_PASSWORD=None

class DevelopmentConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  
class StagingConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:booking-agent-book-load-staging'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:booking-assistant-flow-staging'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-movements-staging'
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-parsed-carrier-staging'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-2:791608169866:mcleod-import-carriers-staging'
class ProductionConfig(Config):
  """Configurations for running in dev mode, with a remote database."""
  PARSED_CARRIER_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-parsed-carrier-prod'  
  BOOK_LOAD_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-agent-book-load-prod'
  BOOKING_ASSISTANT_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:booking-assistant-flow-prod'
  IMPORT_MOVEMENTS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-movements-prod'
  IMPORT_CARRIERS_SNS_TOPIC_ARN = 'arn:aws:sns:us-west-1:791608169866:mcleod-import-carriers-prod'

config_options = {
    'local': LocalConfig,
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}

env_name = os.getenv('APP_SETTINGS')

if not env_name:
  print("warning: No APP_SETTINGS environment variable set, using development")
  env_name = 'development'

app_config = config_options[env_name]
