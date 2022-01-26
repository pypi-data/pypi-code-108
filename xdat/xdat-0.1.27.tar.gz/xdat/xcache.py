import inspect
import functools
import hashlib
import cloudpickle as pickle
import pandas as pd

from . import xsettings
from scriptine import path


def x_cached(name='', hash_key=None, also_parquet=False, outer_level=1):
    def decorator(func):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        calling_name = calframe[outer_level][3]
        if calling_name == '<module>':
            calling_name = path(calframe[outer_level][1]).namebase

        f_src = inspect.getsource(func)
        short_name = name or func.__name__
        f_name = f"{calling_name}__{func.__name__}"
        if name:
            f_name = f"{f_name}__{name}"

        assert xsettings.CACHE_PATH is not None, "must set xsettings.CACHE_PATH"
        cache_folder = xsettings.CACHE_PATH.joinpath(f_name)

        @functools.wraps(func)
        def _cached(*args, **kwargs):
            code_text = f_src + f_name + name + str(hash_key) + str((args, kwargs))
            code_hash = hashlib.md5(code_text.encode('utf-8')).hexdigest()

            cache_subfolder = cache_folder.joinpath(code_hash)
            cache_subfolder.ensure_dir()
            cache_file = cache_subfolder.joinpath(f"{short_name}.pickle")

            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

            results = func(*args, **kwargs)

            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)

            if also_parquet:
                assert isinstance(results, pd.DataFrame), "need DataFrame to save as parquet"
                parquet_path = cache_subfolder.joinpath(f"{short_name}.parquet")
                results.to_parquet(parquet_path, use_deprecated_int96_timestamps=True)

            return results
        return _cached

    return decorator


def x_cached_call(func, *args, name='', hash_key=None, also_parquet=False, **kwargs):
    dec = x_cached(name=name, also_parquet=also_parquet, outer_level=2)
    return dec(func)(*args, **kwargs)
