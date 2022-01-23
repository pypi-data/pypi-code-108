from pytest_docker_fixtures.containers._base import BaseImage
from pytest_docker_fixtures.images import settings
from guillotina import testing
import pytest
import os


def base_settings_configurator(settings):
    if 'applications' in settings:
        settings['applications'].append('guillotina_stripe')
        settings['applications'].append('guillotina_stripe.test_package')
    else:
        settings['applications'] = [
            'guillotina_stripe', 'guillotina_stripe.test_package']
    settings['load_utilities']['stripe'] = {
        "provides": "guillotina_stripe.interfaces.IStripePayUtility",
        "factory": "guillotina_stripe.utility.StripePayUtility",
        "settings": {
            "secret": os.environ.get("STRIPE_KEY", ""),
            "signing": os.environ.get("SIGNING", ""),
            "testing": True
        },
    }
    settings['stripe'] = {
        "subscriptions": {
            "CustomSubscriptionType": [{"trial": 0, "price": "price_1HNb9XGeGvgK89lRkF3KPEgs"}]
        },
        "products": {
            "CustomProductType": ["price_1I0UIuGeGvgK89lReW6fQzYM", "price_1I0UJWGeGvgK89lRf4C1Qt7z"]
        }
    }


testing.configure_with(base_settings_configurator)

settings['stripe'] = {
    'max_wait_s': 30,
    'image': 'stripemock/stripe-mock',
    'version': 'latest',
}


class STRIPE(BaseImage):
    name = 'stripe'
    port = 12112

    def check(self):
        import requests

        conn = None
        cur = None
        try:
            try:
                resp = requests.get(f"https://{self.host}:{self.get_port()}")
                assert resp == 200
            finally:
                pass
            return True
        except Exception:
            return False


stripe_image = STRIPE()


@pytest.fixture(scope='session')
def stripe():
    result = stripe_image.run()
    yield result
    stripe_image.stop()
