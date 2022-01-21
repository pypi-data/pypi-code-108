from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.settings import perform_import

DEFAULTS = {
    # Whether or not to accept data posted to a non-existing collection.
    "ACCEPT_NEW_COLLECTIONS": False,
    # A list of classpaths to implementations of ingress.consumer.IngressConsumer
    # to handle the data in the queue.
    "CONSUMER_CLASSES": [],
    # A list of authentication classes used in the ingress view.
    # See https://www.django-rest-framework.org/api-guide/authentication/
    "AUTHENTICATION_CLASSES": [],
    # A list of permission classes used in the ingress view.
    # See https://www.django-rest-framework.org/api-guide/permissions/
    "PERMISSION_CLASSES": [],
    # Encoding that the data will be in when posted to the ingress
    "ENCODING": "utf-8",
    # Disable all auth permission checks during startup (ie when not using ingress)
    "DISABLE_ALL_AUTH_PERMISSION_CHECKS": False,
}

# Which settings to automatically import upon use
IMPORT_STRINGS = ["PERMISSION_CLASSES", "AUTHENTICATION_CLASSES", "CONSUMER_CLASSES"]


class AppSettings:
    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError(f"Invalid API setting: {attr}")

        # get the setting from the django conf settings (application level)
        try:
            value = getattr(settings, f"INGRESS_{attr}")
        except AttributeError:
            # or obtain a default
            value = DEFAULTS[attr]

        if attr in IMPORT_STRINGS:
            return perform_import(value, attr)
        return value

    def get_consumer_for_collection(self, collection_name):
        consumers = self.CONSUMER_CLASSES or []
        for consumer in consumers:
            if consumer.collection_name == collection_name:
                return consumer

        raise ObjectDoesNotExist(
            f"No consumer exists for collection '{collection_name}'. "
            f"Define it in INGRESS_CONSUMER_CLASSES"
        )


app_settings = AppSettings()
