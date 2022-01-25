import copy
import os.path

from flask.ctx import RequestContext
from werkzeug.exceptions import HTTPException, NotFound
from .config import Option

class RequestContextWithSamStatic(RequestContext):
    def match_request(self) -> None:
        # DEACTIVE flask_samestatic if flask.conf was modified as SAMESTATIC.options.DEACTIVE in other middlewares.
        if self.app.config['SAMSTATIC_ENDPOINTS'] == Option.DEACTIVE:
            return super().match_request()

        def match_certain_rule(rule) -> 'endpoint':
            url_adapter = copy.copy(self.url_adapter)
            url_adapter.map = copy.copy(self.url_adapter.map)
            url_adapter.map._rules = [rule]
            try:
                result = url_adapter.match(return_rule=True)
                url_rule, view_args = result
            except HTTPException as e:
                self.request.routing_exception = e
            else:
                self.request.routing_exception = None
                self.request.url_rule, self.request.view_args = (url_rule, view_args)
                endpoint = url_rule.endpoint
                return endpoint

        def assemble_filepath(endpoint, view_args) -> str:
            if endpoint == 'static':
                static_folder = self.app.static_folder
            else:
                static_folder = self.app.blueprints[endpoint.split('.')[0]].static_folder
            path = os.path.join(static_folder, view_args['filename'])
            return path

        static_endpoints: set = self.app.get_static_endpoints()
        all_static_endpoints: set = self.app.get_static_endpoints(range_='all')

        for rule in self.url_adapter.map._rules:
            endpoint = match_certain_rule(rule)

            if not endpoint: continue
            if endpoint not in all_static_endpoints: return

            # 走到这一步说明匹配到一个static endpoint

            if endpoint not in static_endpoints:
                self.request.routing_exception = HTTPException(f'the static endpoint ({str(endpoint)}) was not in customized range (app.conf["STATIC_ENDPOINTS"])')
                self.request.url_rule, self.request.view_args = (None, None)
                continue

            path = assemble_filepath(endpoint, self.request.view_args)
            if os.path.exists(path):
                break
            else:
                self.request.routing_exception = NotFound(f'{path}')
                self.request.url_rule, self.request.view_args = (None, None)
