import cloudpickle
import sys
import re
import importlib_metadata
import inspect
import base64
import os

_required_dists = set([])
_old_is_registered_pickle_by_value = cloudpickle.cloudpickle._is_registered_pickle_by_value

PKG_TO_DIST = None
def get_dist_name(module_name):
    global PKG_TO_DIST
    if PKG_TO_DIST is None:
        PKG_TO_DIST = importlib_metadata.packages_distributions()
    lst = PKG_TO_DIST.get(module_name, [])
    if len(lst) < 1:
        return None
    return lst[0]

def _is_registered_pickle_by_value(module):
    builtin_regexes = [
        '^.*lib/python[.0-9]+/%s/.*$',
        '^.*lib/python[.0-9]+\\.zip/%s/.*$',
        '^.*lib/python[.0-9]+/lib-dynload/%s/.*$',
        '^.*lib/python[.0-9]+/%s\\.py$',
        '^.*lib/python[.0-9]+\\.zip/%s\\.py$',
        '^.*lib/python[.0-9]+/lib-dynload/%s\\.py$',
    ]
    site_packages_regexes = [
        '^.*lib/python3\\.[.0-9]+/site-packages/%s/.*$',
        '^.*lib/python3\\.[.0-9]+/dist-packages/%s/.*$',
    ]
    module_rootname = module.__name__.split('.')[0]
    module_path = getattr(module, '__file__', None)

    res = _old_is_registered_pickle_by_value(module)
    if module_path is None:
        return res
    elif any(re.match(r % module_rootname, module_path) for r in builtin_regexes):
        return res
    elif any(re.match(r % module_rootname, module_path) for r in site_packages_regexes):
        if not res:
            try:
                dist_name = get_dist_name(module_rootname)
                if dist_name is None:
                    return True
                version = importlib_metadata.version(dist_name)
                _required_dists.add('%s==%s' % (dist_name, version))
            except importlib_metadata.PackageNotFoundError as e:
                return True
        return res
    else:
        return True

_old_module_reduce = cloudpickle.cloudpickle_fast._module_reduce
def _module_reduce_include_env(obj):
    if obj == os:
        if cloudpickle.cloudpickle_fast._should_pickle_by_reference(obj):
            return cloudpickle.cloudpickle_fast.dynamic_subimport, (obj.__name__, {
                'environ': os.environ,
                'environb': os.environb,
            })
    return _old_module_reduce(obj)

def deserialize(obj):
    return cloudpickle.loads(obj['pickled'])

# TODO: add strict mode that uses `pipdeptree` to exactly match
# dependencies of packages as well.
def serialize(obj, custom_modules=[], match_library_patch_version=False, mimic_environ=True, force_versions={}, model_name=None):
    pbv = cloudpickle.list_registry_pickle_by_value().copy()
    try:
        for m in custom_modules:
            if m not in pbv:
                cloudpickle.register_pickle_by_value(m)
        PKG_TO_DIST = None
        _required_dists.clear()
        cloudpickle.cloudpickle._is_registered_pickle_by_value = _is_registered_pickle_by_value
        if mimic_environ:
            cloudpickle.cloudpickle_fast.CloudPickler._dispatch_table[
                cloudpickle.cloudpickle_fast.types.ModuleType
            ] = _module_reduce_include_env
        pickled = cloudpickle.dumps(obj)
    finally:
        cloudpickle.cloudpickle._is_registered_pickle_by_value = _old_is_registered_pickle_by_value
        cloudpickle.cloudpickle_fast.CloudPickler._dispatch_table[
            cloudpickle.cloudpickle_fast.types.ModuleType
        ] = _old_module_reduce
        for m in custom_modules:
            if m not in pbv:
                cloudpickle.unregister_pickle_by_value(m)

    reqs = list(_required_dists)
    reqs.sort()

    possible_names = set([])
    caller_frame = inspect.stack()[2].frame

    if model_name is None:
        # Derive name for model
        varmaps = [caller_frame.f_locals, caller_frame.f_globals]
        for varmap in varmaps:
            for k, v in varmap.items():
                if v is obj:
                    possible_names.add(k)

        if len(possible_names) == 0:
            raise RuntimeError('Unable to infer `model_name`, please specify explicitly.')
        elif len(possible_names) > 1:
            raise RuntimeError(f'Too many possible values for `model_name` '
                            + f'({possible_names}), please specify explicitly.')
        else:
            model_name = possible_names.pop()

    v = sys.version_info
    pyver = f'{v.major}.{v.minor}'
    if match_library_patch_version:
        pyver += f'.{v.micro}'
    else:
        for i in range(len(reqs)):
            reqs[i] = '.'.join(reqs[i].split('.')[:-1] + ['*'])

    reqs = [req for req in reqs if req.split('==')[0] not in force_versions]
    reqs += [f'{k}=={v}' for k, v in force_versions.items()]
    res = {
        'model_name': model_name,
        'pyver': pyver,
        'reqs': reqs,
    }
    return res, pickled
