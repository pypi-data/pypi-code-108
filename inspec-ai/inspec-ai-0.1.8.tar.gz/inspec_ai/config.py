import os

TRACKING_DISABLED = os.getenv('INSPEC_DISABLE_TRACKING', "False").lower() in ['true', '1', 'yes', 'y']
