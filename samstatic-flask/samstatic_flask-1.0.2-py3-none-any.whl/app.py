from functools import lru_cache

from flask import Flask
from flask.ctx import RequestContext

from .config import Option
from .ctx import RequestContextWithSamStatic
from .helper import set_samstatic_default_parm

class FlaskWithSamStatic(Flask):
    def __init__(self, *Flask_args, **Flask_kwargs):
        super().__init__(*Flask_args, **Flask_kwargs)
        set_samstatic_default_parm(self)

    def request_context(self, environ: dict) -> RequestContext:
        # DEACTIVE flask_samestatic if flask.conf was modified as SAMESTATIC.options.DEACTIVE in other middlewares.
        if self.config.get('SAMSTATIC_ENDPOINTS', Option.ALL) == Option.DEACTIVE:
            return Flask.request_context(self, environ)  # don't use super() as it's not compatible with MethodType(...)

        return RequestContextWithSamStatic(self, environ)

    def get_static_endpoints(self, range_:str = 'config') -> set:
        if self.config['SAMSTATIC_ENDPOINTS_USE_CACHE']:
            if self._samstatic_endpoints_caches[range_]:
                print('use cache', range_)
                return self._samstatic_endpoints_caches[range_]

        def get_all_static_endpoints():
            static_endpoints = ['static']
            static_endpoints.extend([bp.name + '.static' for bp in self.blueprints.values()])
            self._samstatic_endpoints_caches['all'] = static_endpoints
            return set(static_endpoints)

        if range_ not in ['config', 'all']:
            raise TypeError('range_ of should be "config" or "all"')

        if range_ == 'all':
            return get_all_static_endpoints()

        # app.config['SAMSTATIC_ENDPOINTS']
        raw_static_endpoints = self.config['SAMSTATIC_ENDPOINTS']
        if raw_static_endpoints in [Option.ALL, (Option.ALL,)]:
            static_endpoints = get_all_static_endpoints()
        elif raw_static_endpoints in [Option.DEACTIVE, (Option.DEACTIVE,)]:
            static_endpoints = {'static'}
        elif raw_static_endpoints[0] == Option.ALLOWED:
            static_endpoints = self.get_static_endpoints(range_='all') & set(raw_static_endpoints[1])
        elif raw_static_endpoints[0] == Option.DISALLOWED:
            static_endpoints = self.get_static_endpoints(range_='all') - set(raw_static_endpoints[1])
        else:
            raise TypeError(f'Type of SAMSTATIC_ENDPOINTS is not supported!')

        self._samstatic_endpoints_caches[range_] = static_endpoints
        return static_endpoints

