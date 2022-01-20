
from kortical.api import _api, code, data, deployment, experiment_framework, instance, model, superhuman_calibration
from kortical.config import kortical_config


def init(url=None, credentials=None, reset_config=False):
    if reset_config:
        kortical_config.reset(url, credentials)
    return _api.init(url, credentials)


def get(url, *args, throw=True, **kwargs):
    kwargs['throw'] = throw
    return _api.get(url, *args, **kwargs)


def post(url, *args, throw=True, **kwargs):
    kwargs['throw'] = throw
    return _api.post(url, *args, **kwargs)


def delete(url, *args, throw=True, **kwargs):
    kwargs['throw'] = throw
    return _api.delete(url, *args, **kwargs)


def post_file(url, fields, filename, filepath, *args, description=None, throw=True, **kwargs):
    kwargs['throw'] = throw
    kwargs['description'] = description
    return _api.post_file(url, fields, filename, filepath, *args, **kwargs)
