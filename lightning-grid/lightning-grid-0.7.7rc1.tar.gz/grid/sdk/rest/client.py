from grid.openapi import (
    ApiClient, AuthServiceApi, ClusterServiceApi, DatastoreServiceApi, RunServiceApi, SAMLOrganizationsServiceApi,
    SessionServiceApi, TensorboardServiceApi, ExperimentServiceApi
)
import grid.sdk.env as env

KNOWN_RETURN_NONE_METHODS_AND_RESPONSE_CLASSES = {'session_service_delete_session': 'V1DeleteSessionResponse'}


def log_method_call_args_and_results(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            inputs = {
                "func": func.__name__,
                "args": [str(x) for x in args],
                "kwargs": {k: str(v)
                           for k, v in kwargs.items()},
            }
            logger.info(f'>>> {pickle.dumps(inputs, pickle.HIGHEST_PROTOCOL)}')

            ret = func(self, *args, **kwargs)

            if func.__name__ in KNOWN_RETURN_NONE_METHODS_AND_RESPONSE_CLASSES:
                if ret is not None:
                    raise ValueError(f'func: {func.__name__} is known to return None, but returned: {ret}')
                outputs = {
                    "type": KNOWN_RETURN_NONE_METHODS_AND_RESPONSE_CLASSES[func.__name__],
                    "data": {},
                }
            else:
                outputs = {
                    "type": ret.__class__.__name__,
                    "data": ret.to_dict(),
                }

            logger.info(f'<<< {func.__name__} {pickle.dumps(outputs, pickle.HIGHEST_PROTOCOL)}')
        except:
            ret = None
        return ret

    return wrapper


if env.TESTING:
    from functools import wraps
    import logging
    import pickle

    logger = logging.getLogger(__name__)

    class _GridRestClientAdapter(
        AuthServiceApi,
        ClusterServiceApi,
        DatastoreServiceApi,
        RunServiceApi,
        SAMLOrganizationsServiceApi,
        SessionServiceApi,
        TensorboardServiceApi,
        ExperimentServiceApi,
    ):
        def __init_subclass__(cls, **kwargs):
            for method in dir(cls):
                if callable(getattr(cls, method)) and not method.startswith('__'):
                    setattr(cls, method, log_method_call_args_and_results(getattr(cls, method)))

    class GridRestClient(_GridRestClientAdapter):
        api_client: ApiClient

        grid_settings_path: str = '.grid/settings.json'
        grid_credentials_path: str = '.grid/credentials.json'

        def __init__(self, api_client: ApiClient):  # skipcq: PYL-W0231
            self.api_client = api_client
else:

    class GridRestClient(
        AuthServiceApi,
        ClusterServiceApi,
        DatastoreServiceApi,
        RunServiceApi,
        SAMLOrganizationsServiceApi,
        SessionServiceApi,
        TensorboardServiceApi,
        ExperimentServiceApi,
    ):
        api_client: ApiClient

        grid_settings_path: str = '.grid/settings.json'
        grid_credentials_path: str = '.grid/credentials.json'

        def __init__(self, api_client: ApiClient):  # skipcq: PYL-W0231
            self.api_client = api_client
