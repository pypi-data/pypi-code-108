import copy
import requests
import json
import sys
import base64
import time
import math
from tqdm import tqdm

from . import config, thunk, errors
from . import json_utils

# We pull these into the toplevel, but the module resolution can't
# know that.
SHORTENS = {
    'client.Client': 'Client',
    'client.Models': 'Models',
}
def repr_classname(obj):
    classname = obj.__class__.__qualname__
    maybe_module = getattr(obj.__class__, '__module__')
    if maybe_module is not None:
        classname = maybe_module + '.' + classname
    for k, v in SHORTENS.items():
        if classname.endswith(k):
            classname = classname[:-len(k)] + v
            break
    return classname

class Censored():
    def __repr__(self):
        return '...'
def repr_with_args(obj, kwargs):
    # We don't want API keys accidentally ending up in logs.
    if 'api_key' in kwargs and kwargs['api_key'][0] != kwargs['api_key'][1]:
        kwargs['api_key'] = (Censored(), None)
    argstr = ', '.join(f'{k}={repr(v[0])}' for k, v in kwargs.items() if v[0] != v[1])
    return f'{repr_classname(obj)}({argstr})'

# We have this extra level of abstraction to make life easier on the testing harness.
class Server():
    pass

class HttpServer(Server):
    def __init__(self, prefix_path):
        self.prefix_path = prefix_path

    def post(self, endpoint, body_json, auth):
        return requests.post(
            self.prefix_path+endpoint,
            headers={
                "Content-Type": 'application/json',
            },
            data=body_json,
            auth=auth,
        )

    def upload_blob(self, endpoint, blob, auth):
        return requests.post(
            self.prefix_path+endpoint,
            data=blob,
            auth=auth,
        )

    def get(self, endpoint, auth):
        return requests.get(
            self.prefix_path+endpoint,
            headers={"Content-Type": 'application/json'},
            auth=auth,
        )

    def __str__(self):
        return self.prefix_path

    def __repr__(self):
        return f'{repr_classname(self)}({repr(self.prefix_path)})'

class EndpointWrapper():
    def __init__(self, server):
        if isinstance(server, str):
            self.server = HttpServer(server)
        else:
            self.server = server

    def post(self, endpoint, obj):
        res = self.server.post(endpoint, obj, self.auth())
        return errors.json_or_err(res)

    def upload_blob(self, endpoint, blob):
        res = self.server.upload_blob(endpoint, blob, self.auth())
        return errors.json_or_err(res)

    def get(self, endpoint):
        res = self.server.get(endpoint, self.auth())
        return errors.json_or_err(res)

    def auth(self):
        return (self.api_key, '')

class CachedRepr:
    def __init__(self, _repr):
        self.__dmn_repr__ = _repr

    def __repr__(self):
        return self.__dmn_repr__

class Models(EndpointWrapper):
    def __init__(self, api_key=None, model_server=None, serialization_fallback=None,
                 stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(config.get_default('model_server', model_server, 'Models'))
        self.api_key = config.get_default('api_key', api_key, 'Models')
        self.namespace = 'default'
        self.serialization_fallback = serialization_fallback
        self.stdout = stdout
        self.stderr = stderr
        self._repr = repr_with_args(self, {
            'api_key': (api_key, None),
            'model_server': (model_server, None),
            'serialization_fallback': (serialization_fallback, None),
            'stdout': (stdout, sys.stdout),
            'stderr': (stderr, sys.stderr),
        })

    def __call__(self, namespace='default'):
        if namespace == 'default':
            return NamespacedModels(
                f'{self.__repr__()}()',
                models=self,
                namespace=namespace,
            )
        else:
            return NamespacedModels(
                f'{self.__repr__()}({repr(namespace)})',
                models=self,
                namespace=namespace,
            )


    def _call_remote(self, namespace, model_name, obj, **kw):
        endpoint = f'v1/call/{namespace}/{model_name}'
        if 'version' in kw:
            endpoint += f':{kw["version"]}'

        body_json = json.dumps(obj)

        res = self.post(endpoint, body_json)
        if res['success']:
            if 'stdout' in res:
                bstr = base64.b64decode(res['stdout']['bytes'])
                if hasattr(self.stdout, 'buffer'):
                    self.stdout.buffer.write(bstr)
                    self.stdout.buffer.flush()
                else:
                    self.stdout.write(bstr.decode('utf-8', errors='replace'))
                    self.stdout.flush()
            if 'stderr' in res:
                bstr = base64.b64decode(res['stderr']['bytes'])
                if hasattr(self.stderr, 'buffer'):
                    self.stderr.buffer.write(bstr)
                    self.stderr.buffer.flush()
                else:
                    self.stderr.write(bstr.decode('utf-8', errors='replace'))
                    self.stderr.flush()
            return json_utils.loads(res['res'])
        else:
            raise errors.RemoteCallError(f'{self.server}{endpoint}', res)

    def __repr__(self):
        return self._repr

class NamespacedModels(CachedRepr):
    def __init__(self, _repr, **kw):
        super().__init__(_repr)
        self.__dmn__ = kw

    def __getattr__(self, model_name):
        return ModelView(
            f'{self.__repr__()}.{model_name}',
            model_name=model_name,
            method=[],
            **self.__dmn__,
        )

class VersionedModelView(CachedRepr):
    def __init__(self, _repr, **kw):
        super().__init__(_repr)
        self.__dmn__ = kw
        self.__dmn__.setdefault('methodless_repr', _repr)

    def __call__(self, *a, **kw):
        sf = self.__dmn__['models'].serialization_fallback
        return self.__dmn__['models']._call_remote(
            obj={
                'args': json_utils.dumps(a, serialization_fallback=sf),
                'kwargs': json_utils.dumps(kw, serialization_fallback=sf),
                'method': self.__dmn__['method'],
            },
            **self.__dmn__,
        )

    def __getattr__(self, method_part):
        no_method = self.__dmn__.copy()
        del no_method['method']
        return VersionedModelView(
            f'{self.__repr__()}.{method_part}',
            method=(self.__dmn__['method']+[method_part]),
            **no_method,
        )

class ModelView(VersionedModelView):
    def __init__(self, _repr, **kw):
        super().__init__(_repr, **kw)

    def __getitem__(self, version):
        return VersionedModelView(
            f'{self.__repr__()}[{repr(version)}]',
            version=version,
            **self.__dmn__,
        )

class Client(EndpointWrapper):
    def __init__(self, api_key=None, admin_server=None, model_server=None, app_server=None, serialization_fallback=None, pre_upload=True, build_mode='kaniko', stdout=sys.stdout, stderr=sys.stderr):
        super().__init__(config.get_default('admin_server', admin_server, 'Client'))
        self.api_key = config.get_default('api_key', api_key, 'Client')
        self.models = Models(self.api_key, model_server=model_server, serialization_fallback=serialization_fallback, stdout=stdout, stderr=stderr)
        self.app_server = config.get_default('app_server', app_server, 'Client')
        self.pre_upload = pre_upload
        self.build_mode = build_mode
        self._repr = repr_with_args(self, {
            'api_key': (api_key, None),
            'admin_server': (admin_server, None),
            'model_server': (model_server, None),
            'serialization_fallback': (serialization_fallback, None),
            'pre_upload': (pre_upload, True),
            'build_mode': (build_mode, 'kaniko'),
            'stdout': (stdout, sys.stdout),
            'stderr': (stderr, sys.stderr),
        })
        self.models._repr = self._repr + '.models'

    def deploy_status(self, master, version):
        return self.post('v1/deploy_status',
                         json.dumps({'master': master, 'version': version}))

    def deploy(self, obj, namespace='default', model_name=None, serialize_opts={}, quiet=False):
        if isinstance(obj, VersionedModelView):
            if obj.__dmn__['method'] != []:
                raise RuntimeError(
                    'Only top-level models can be redeployed.  ' +
                    f'Instead of deploying {repr(obj)}, deploy ' +
                    f'{obj.__dmn__["methodless_repr"]}.')
            res = self.post(
                f'v1/redeploy',
                json.dumps({
                    'namespace': namespace,
                    'model_name': model_name or obj.__dmn__['model_name'],

                    'from_namespace': obj.__dmn__['namespace'],
                    'from_model_name': obj.__dmn__['model_name'],
                    'from_version': obj.__dmn__.get('version', None),
                }),
            )
        else:
            deploy_args, pickled = thunk.serialize(
                obj, model_name=model_name, **serialize_opts)
            deploy_args['namespace'] = namespace
            if self.build_mode is not None:
                deploy_args['build_mode'] = self.build_mode
            if self.pre_upload:
                res = self.upload_blob('v1/upload', pickled)
                deploy_args['pickled_ref'] = res['ref']
            else:
                deploy_args['pickled_b64'] = base64.encodebytes(pickled).decode('utf-8')
            res = self.post('v1/deploy', json.dumps(deploy_args))

        deploy_status = DeployStatus(self, data=res, quiet=quiet)
        if not quiet and deploy_status.url is not None:
            print("Deploy in progress.  Watch here: " + deploy_status.url)
        return deploy_status

    def __repr__(self):
        return self._repr

    def endpoints(self):
        return self.get('v1/endpoints')

def soft_progress(elapsed, expected):
    return (1/(1+math.e**-((2*elapsed)/expected))-0.5)*2
BAR_FORMAT = '{desc}{percentage:3.0f}%|{bar}| [{elapsed}<{remaining}{postfix}]'

class DeployStatus:
    def __init__(self, client, data, quiet, app_server=None):
        self.client = client
        self.data = data
        self.expected = data.get('deploy_time_estimate', 60)

        self.quiet = quiet
        self.as_of = time.time()

        self.url = None
        if self.data.get('deploy', None) is not None:
            self.url = f"{self.client.app_server}deploy_status/{self.data['deploy']['master']}/{self.data['deploy']['version']}"

    def __repr__(self):
        return f'DeployStatus(as_of={self.as_of}, data={self.data}, url={repr(self.url)})'
    def has_condition(self, condition):
        return condition in self.data['conditions']

    def refresh(self):
        self.as_of = time.time()
        self.data = self.client.deploy_status(**self.data['deploy'])
        return self

    def wait(self, condition='ready', error_if_superseded=True,
             quiet=None, timeout=3600, sleep_time=1, max_sleep_time=60):
        if quiet is None:
            quiet = self.quiet
        if condition is None:
            condition = 'ready'
        legal_conditions = ['ready', 'stable']
        if condition not in legal_conditions:
            raise RuntimeError(
                f'`condition` must be in `{legal_conditions}`, got `{condition}`.')

        start_time = time.time()
        cur_sleep_time = sleep_time
        last = 0
        if quiet:
            rendered_bar = None
        else:
            rendered_bar = tqdm(bar_format=BAR_FORMAT, total=1)
        with rendered_bar as pbar:
            while not self.has_condition(condition):
                self.refresh()
                cur_time = time.time()
                if self.has_condition('failed'):
                    raise RuntimeError(f'Deploy failed: {self}')
                if self.has_condition('superseded'):
                    if error_if_superseded:
                        raise RuntimeError(
                            f'Deploy superseded by a later deploy: {self}')
                if cur_time > start_time + timeout:
                    raise TimeoutError(
                        f'Timed out waiting for condition `{condition}`.')
                res = soft_progress(cur_time - start_time, self.expected)
                if pbar is not None:
                    pbar.set_postfix({'conditions': self.data['conditions']})
                    pbar.update(res - last)
                last = res
                time.sleep(cur_sleep_time)
                cur_sleep_time = min(1.05*cur_sleep_time, max_sleep_time)
            if pbar is not None:
                pbar.update(1 - last)

        return self
