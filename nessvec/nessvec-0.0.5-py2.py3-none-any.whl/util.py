""" Utilities for loading word2vec and GloVe word embeddings for vector reasoning

STANFORD_GLOVE_URLS = [
    'https://nlp.stanford.edu/data/glove.6B.zip',
    'https://nlp.stanford.edu/data/glove.42B.300d.zip',
    'https://nlp.stanford.edu/data/glove.840B.300d.zip',
    'https://nlp.stanford.edu/data/glove.twitter.27B.zip',
]

References:
  * https://nlp.stanford.edu/projects/glove/
  * https://nlp.stanford.edu/pubs/
  * https://nlp.stanford.edu/software/

"""
import re

import pandas as pd
import numpy as np
import logging

from nessvec.files import load_glove, DATA_DIR

log = logging.getLogger(__name__)

if not DATA_DIR.is_dir():
    DATA_DIR.mkdir()

# size: 6B | 42B | 84B | twitter.27B
GLOVE_ZIP_FILENAME_TEMPLATE = 'glove.{size}B.zip'
GLOVE_URL_TEMPLATE = 'http://nlp.stanford.edu/data/' + GLOVE_ZIP_FILENAME_TEMPLATE

# dim: 50 | 100 | 300 | 1000
GLOVE_FILENAME_TEMPLATE = 'glove.{size}B.{dim}d.txt'


STANFORD_GLOVE_URLS = [
    'https://nlp.stanford.edu/data/glove.6B.zip',
    'https://nlp.stanford.edu/data/glove.42B.300d.zip',
    'https://nlp.stanford.edu/data/glove.840B.300d.zip',
    'https://nlp.stanford.edu/data/glove.twitter.27B.zip',
]


def glove_normalize(s):
    """ GloVe deletes whitespace instead of replacing with "_" (Word2Vec style)

    >>> glove_normalize('Los Angeles')
    'losangeles'
    """
    return re.sub(r'\s+', '', s).lower()


def word2vec_normalize(s):
    """ Word2Vec replaces whitespace with "_"

    >>> word2vec_normalize('Los Angeles')
    'Los_Angeles'
    """
    return re.sub(r'\s+', '_', s)


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


def cosine_similarities(target, components):
    """ 1 - cos(angle_between(target, components)) where b is a matrix of vectors

    >>> cosine_similarities(target=[1,2,3], components=[[3, 4, 5], [-1,3,-2]])
    array([ 0.98..., -0.07...])
    """
    # target = 'the'
    # components = 'one two the oregon'.split()
    # target = wv[target] if isinstance(target, str) else target
    # components = np.array([wv[c] for c in components]) if isinstance(components[0], str) else components
    target = normalize_vector(np.array(target).flatten())
    target = target.reshape((-1, 1))
    components = np.array(components)
    n_vecs, n_dims = components.shape
    if n_dims != target.shape[0] and target.shape[0] == n_vecs:
        components = components.T
        n_vecs, n_dims = components.shape()

    target = normalize_vector(target)
    # print(target.shape)
    norms = np.linalg.norm(components, axis=1).reshape(n_vecs, 1)
    # norms = norms.dot(np.ones((1, n_dims)))
    log.debug(norms)
    log.debug(components)
    components = components / norms
    # print(components.shape)
    return components.dot(target).flatten()


class IndexedVectors:
    def __init__(self, vectors=None, index=None, normalizer=glove_normalize):
        self.normalizer = normalizer
        if vectors is None:
            self.load()
        elif isinstance(vectors, dict):
            self.df = pd.DataFrame(vectors)
        else:
            self.df = pd.DataFrame(vectors, index=(index or range(len(vectors))))

    def load(self, dim=50, size=6):
        self.df = pd.DataFrame(load_glove(dim=dim, size=size))
        return self

    def get(self, key, default=None):
        if key in self.df.columns:
            return self.df[key]
        return default

    def __getitem__(self, key):
        try:
            return self.df[key]
        except KeyError:
            print(f"Unable to find '{key}' in {self.df.shape} DataFrame of vectors")
        normalized_key = self.normalizer(str(key))
        try:
            return self.df[normalized_key]
        except KeyError:
            print(f"Unable to find '{normalized_key}' in {self.df.shape} DataFrame of vectors")
        raise(KeyError(f"Unable to find any of {set([key, normalized_key])} in self.df.shape DataFrame of vectors"))

    def keys(self):
        return self.df.columns.values

    def values(self):
        return self.df.T.values

    def iteritems(self):
        return self.df.T.iterrows()

    def iterrows(self):
        return self.df.T.iterrows()
