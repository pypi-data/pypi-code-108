# import random
from annoy import AnnoyIndex
from nessvec.files import load_glove
from tqdm import tqdm

import pandas as pd
import numpy as np

import logging

log = logging.getLogger(__name__)


def normalize_vector(x):
    """ Convert to 1-D np.array and divide vector by it's length (2-norm)

    >>> normalize_vector([0, 1, 0])
    array([0., 1., 0.])
    >>> normalize_vector([1, 1, 0])
    array([0.707..., 0.707..., 0...])
    """
    # x = np.array(x).flatten()
    xnorm = np.linalg.norm(x) or 1
    xnorm = xnorm if np.isfinite(xnorm) else 1
    return x / xnorm


def cosine_similarity(a, b):
    """ 1 - cos(angle_between(a, b))

    >>> cosine_similarity([0, 1, 1], [0, 1, 0])  # 45 deg
    0.707...
    """
    a = normalize_vector(np.array(a).flatten())
    b = normalize_vector(np.array(b).flatten())
    return (a * b).sum()


def quantize(value, bins, default_bin=0):
    if value in range(len(bins)):
        return bins[value]
    elif value in bins:
        return value
    else:
        for s in bins:
            if value >= s:
                return s
    return bins[default_bin]


class WordVectors(dict):

    sizes = [6, 42, 84]
    dimensionalities = [50, 100, 300, 1000]

    def __init__(self, num_dims=0, size=0, num_trees=10, w2v=None):
        self.num_dims = quantize(value=num_dims, bins=self.dimensionalities)
        self.billions_of_words = quantize(value=size, bins=self.sizes)
        if w2v is None:
            self.w2v = load_glove(self.num_dims, self.billions_of_words)
            log.error(f'load_glove {self.w2v}')
        else:
            self.w2v = w2v
            log.error(f'use existing {self.w2v}')

        # TODO: ensure this doesn't create 2 independent dicts (2x memory)
        self.update(self.w2v)
        self.i2w = list(self.w2v.keys())
        self.num_vecs = len(self.w2v)
        self.num_dims = len(self.w2v[next(iter(self.w2v.keys()))])

        self.idx = AnnoyIndex(len(self.w2v['the']), 'angular')

        log.info(f'Building index on {self.num_vecs} {self.num_dims}-D vectors')
        for i, v in tqdm(enumerate(self.w2v.values())):
            self.idx.add_item(i, v)

        self.idx.build(num_trees)
        self.w2i = dict(zip(self.i2w, range(self.num_vecs)))

    def ensure_vector(self, w):
        """ For str w, return a single wordvector for the given str otherwise return w

        >>> wv = WordVectors()
        >>> wv.ensure_vector('portland seattle').shape
        (50,)
        >>> all(wv.ensure_vector('portland nonwordything') == wv.ensure_vector('portland'))
        True
        """
        if isinstance(w, str):
            ngram = w.split()
            if len(ngram) == 1:
                return self.w2v[ngram[0]]
            return pd.DataFrame([np.array(self.w2v[onegram]) for onegram in ngram if onegram in self.w2v]).mean().values
        else:
            return np.array(w)
        return np.array(w)

    def cosine_similarity(self, w1, w2):
        a = self.ensure_vector(w1)
        b = self.ensure_vector(w2)
        return cosine_similarity(a, b)

    def save(self):
        self.idx.save(f'glove_{self.num_vecs}x{self.num_dims}.ann')

    def find_similar(self, w, n=10):
        return [self.i2w[i] for i in self.idx.get_nns_by_item(self.w2i[w], n)]


if __name__ == "__main__":
    # idx = WordVectors()
    # seattle = idx.w2v['seattle']
    pass
