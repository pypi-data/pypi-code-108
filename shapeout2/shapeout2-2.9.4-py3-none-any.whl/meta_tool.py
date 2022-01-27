"""Convenience methods to retrieve meta data from .rtdc files"""
import functools
import dclab


def get_info(path, section, key):
    config = get_rtdc_config(path)
    return config[section][key]


def get_repr(path, append_path=False):
    """representative string of a dataset"""
    exp = get_rtdc_config(path)["experiment"]
    rep = "{} #{} ({} {})".format(exp["sample"],
                                  exp["run index"],
                                  exp["date"],
                                  exp["time"])
    if append_path:
        rep += "\n{}".format(path)
    return rep


@functools.lru_cache(maxsize=100)
def get_rtdc_config(path):
    with dclab.new_dataset(path) as ds:
        config = ds.config.copy()
    return config


@functools.lru_cache(maxsize=100)
def get_rtdc_features(path, scalar=True, only_loaded=False):
    """Return available features in a dataset"""
    av_feat = []
    with dclab.new_dataset(path) as ds:
        if scalar:
            features = ds.features_scalar
        else:
            features = ds.features
        for feat in features:
            if only_loaded:
                if feat in ds.features_loaded:
                    av_feat.append(feat)
            else:
                if feat in ds:
                    av_feat.append(feat)
    return av_feat


def get_rtdc_features_bulk(paths, scalar=True):
    """Return available features for a list of dataset paths"""
    features = []
    for pp in paths:
        features += get_rtdc_features(path=pp, scalar=scalar)
    return sorted(set(features))


@functools.lru_cache(maxsize=10000)
def get_rtdc_features_minmax(path, *features):
    """Return dict with min/max of scalar features in a dataset"""
    mmdict = {}
    with dclab.new_dataset(path) as ds:
        if len(features) == 0:
            features = ds.features_loaded
        for feat in features:
            assert dclab.dfn.scalar_feature_exists(feat)
            if feat in ds:
                mmdict[feat] = ds[feat].min(), ds[feat].max()
    return mmdict


def get_rtdc_features_minmax_bulk(paths, features=[]):
    """Perform `get_rtdc_features_minmax` on a list of paths

    Parameters
    ----------
    paths: list of str or list of pathlib.Path
        Paths to measurement files
    features: list of str or empty list
        Names of the features to compute the min/max values for.
        If empty, all loaded features will be used.
    """
    mmdict = {}
    for pp in paths:
        mmdi = get_rtdc_features_minmax(pp, *features)
        for feat in mmdi:
            if feat in mmdict:
                fmin = min(mmdict[feat][0], mmdi[feat][0])
                fmax = max(mmdict[feat][1], mmdi[feat][1])
                mmdict[feat] = (fmin, fmax)
            else:
                mmdict[feat] = mmdi[feat]
    return mmdict
