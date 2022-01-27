import os
try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:
    from urlparse import urlsplit, urlunsplit


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class Environment:
    ROXY_INTERNAL_PATH = 'device/request_configuration'

    PATHS = {
        'QA': {
            'CDN_PATH': 'https://qa-conf.rollout.io',
            'API_PATH': 'https://qa-api.rollout.io/device/get_configuration',
            'CDN_STATE_PATH': 'https://qa-statestore.rollout.io',
            'API_STATE_PATH': 'https://qa-api.rollout.io/device/update_state_store',
            'ANALYTICS_PATH': 'https://qaanalytic.rollout.io',
            'NOTIFICATIONS_PATH': 'https://qax-push.rollout.io/sse'
        },
        'LOCAL': {
            'CDN_PATH': 'https://development-conf.rollout.io',
            'API_PATH': 'http://127.0.0.1:8557/device/get_configuration',
            'CDN_STATE_PATH': 'https://development-statestore.rollout.io',
            'API_STATE_PATH': 'http://127.0.0.1:8557/device/update_state_store',
            'ANALYTICS_PATH': 'http://127.0.0.1:8787',
            'NOTIFICATIONS_PATH': 'http://127.0.0.1:8887/sse'
        },
        'DEFAULT': {
            'CDN_PATH': 'https://conf.rollout.io',
            'API_PATH': 'https://x-api.rollout.io/device/get_configuration',
            'CDN_STATE_PATH': 'https://statestore.rollout.io',
            'API_STATE_PATH': 'https://x-api.rollout.io/device/update_state_store',
            'ANALYTICS_PATH': 'https://analytic.rollout.io',
            'NOTIFICATIONS_PATH': 'https://push.rollout.io/sse'
        }
    }

    @classproperty
    def CDN_PATH(self):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['CDN_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['CDN_PATH']
        return Environment.PATHS['DEFAULT']['CDN_PATH']

    @staticmethod
    def API_PATH(server_url='https://x-api.rollout.io'):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['API_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['API_PATH']
        
        if server_url is not 'https://x-api.rollout.io':
            Environment.PATHS['DEFAULT']['API_PATH'] = '%s/device/get_configuration' % server_url
        return Environment.PATHS['DEFAULT']['API_PATH']

    @classproperty
    def CDN_STATE_PATH(self):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['CDN_STATE_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['CDN_STATE_PATH']

        return Environment.PATHS['DEFAULT']['CDN_STATE_PATH']

    @staticmethod
    def API_STATE_PATH(server_url='https://x-api.rollout.io'):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['API_STATE_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['API_STATE_PATH']

        if server_url is not 'https://x-api.rollout.io':
            Environment.PATHS['DEFAULT']['API_STATE_PATH'] = '%s/device/update_state_store' % server_url
        return Environment.PATHS['DEFAULT']['API_STATE_PATH']

    @classproperty
    def ANALYTICS_PATH(self):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['ANALYTICS_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['ANALYTICS_PATH']

        return Environment.PATHS['DEFAULT']['ANALYTICS_PATH']

    @classproperty
    def NOTIFICATIONS_PATH(self):
        rollout_mode = os.getenv('ROLLOUT_MODE', '')
        if rollout_mode == 'QA':
            return Environment.PATHS['QA']['NOTIFICATIONS_PATH']
        elif rollout_mode == 'LOCAL':
            return Environment.PATHS['LOCAL']['NOTIFICATIONS_PATH']

        return Environment.PATHS['DEFAULT']['NOTIFICATIONS_PATH']

    @staticmethod
    def ADD_PREFIX_TO_URL(prefix, url):
        list_url = list(urlsplit(url))
        updated_url = '{}-{}'.format(prefix, list_url[1])
        list_url[1] = updated_url
        new_url = urlunsplit(list_url)
        return new_url

    @staticmethod
    def SWITCH_TO_REGION_HOSTING(hosting):
        if hosting is 'eu':
            Environment.PATHS['QA']['API_PATH'] = Environment.ADD_PREFIX_TO_URL(hosting, Environment.PATHS['QA']['API_PATH'])
            Environment.PATHS['DEFAULT']['API_PATH'] = Environment.ADD_PREFIX_TO_URL(hosting, Environment.PATHS['DEFAULT']['API_PATH'])
            Environment.PATHS['QA']['API_STATE_PATH'] = Environment.ADD_PREFIX_TO_URL(hosting, Environment.PATHS['QA']['API_STATE_PATH'])
            Environment.PATHS['DEFAULT']['API_STATE_PATH'] = Environment.ADD_PREFIX_TO_URL(hosting, Environment.PATHS['DEFAULT']['API_STATE_PATH'])

