import pickle
from hashlib import md5
from scriptine import path

from .xcache import x_cached_call

"""
https://github.com/stan-dev/pystan2
https://pystan2.readthedocs.io/en/latest/
"""


def cached(model_code=None, model_path=None, model_name=None, cache_folder='/tmp', **kwargs):
    """Use just as you would `stan`"""
    import pystan

    assert model_code or model_path
    cache_folder = path(cache_folder)
    if model_path:
        model_path = path(model_path).abspath()
        print(f'Stan model: {model_path}')
        with open(model_path, "r") as f:
            model_code = f.read()

    code_hash = md5(model_code.encode('ascii')).hexdigest()
    if model_name is None:
        cache_fn = 'cached-model-{}.pkl'.format(code_hash)
    else:
        cache_fn = 'cached-{}-{}.pkl'.format(model_name, code_hash)

    cache_fn = cache_folder.joinpath(cache_fn)
    try:
        sm = pickle.load(open(cache_fn, 'rb'))
    except:
        sm = pystan.StanModel(model_code=model_code, **kwargs)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
    else:
        print("Using cached StanModel")
    return sm
