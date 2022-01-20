from environs import Env

env = Env()


API_URL = env("ADUMO_API_URL", default="https://staging-apiv2.adumoonline.com/")
CLIENT_ID = env("ADUMO_CLIENT_ID", default="9ba5008c-08ee-4286-a349-54af91a621b0")
CLIENT_SECRET = env(
    "ADUMO_CLIENT_SECRET", default="23adadc0-da2d-4dac-a128-4845a5d71293"
)
APPLICATION_ID = env(
    "ADUMO_APPLICATION_ID", default="23ADADC0-DA2D-4DAC-A128-4845A5D71293"
)
MERCHANT_UID = env("ADUMO_MERCHANT_UID", default="9BA5008C-08EE-4286-A349-54AF91A621B0")

DEFAULT_IP_ADDRESS = env("ADUMO_ORIGIN_IP", default="192.168.0.1")
