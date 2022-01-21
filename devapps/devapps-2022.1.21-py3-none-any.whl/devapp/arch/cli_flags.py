"""
# Multi Purpose Flags

Additionally we have log_level, ... flags, defined in structlogging.sl
"""
from devapp.app import FLG, flag


def oauth():

    # e.g. gitlab, cloudfoundry
    flag.string('username', '', 'Username')
    flag.string('endpoint_name', 'default', 'You may have more endpoints')
    flag.string('endpoint', '', 'API Endpoint')

    def get_endpoint(example='https://example.gitlab.com'):
        import requests
        from devapp.spec.os_tools import env_get_interactive_write as envget

        def vld(k, url):
            try:
                if requests.get(url).status_code == 200:
                    return 'write'
            except:
                print('Not reachable')
                return

        return FLG.endpoint or envget('DA_URL_GITLAB', validate=vld, example=example)

    return get_endpoint
