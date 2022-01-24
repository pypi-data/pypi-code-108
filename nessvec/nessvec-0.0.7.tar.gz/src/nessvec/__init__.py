# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = 'unknown'
finally:
    del get_distribution, DistributionNotFound


from nessvec import util
from nessvec import files  # noqa
# from nessvec import hypervec  # requires annoy.AnnoyIndex
from nessvec import glove


__all__ = ['util', 'files', 'glove']  # , hypervec]
# from nessvec import nessvectors as word2vec  # noqa
