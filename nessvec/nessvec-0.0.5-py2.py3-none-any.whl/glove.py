""" From chapter 6 about the "ness" of word vectors:

Compose a word vector for each "ness" like placeness, humanness, femaleness, etc
Provide a nessvector for any given word

>>> nessvector('Seattle')
placeness      0.257971
peopleness    -0.059435
animalness    -0.014691
conceptness    0.175459
femaleness    -0.359303
dtype: float64
>>> nessvector('Portland')
placeness      0.365310
peopleness    -0.198677
animalness     0.065087
conceptness    0.020675
femaleness    -0.252396
dtype: float64
>>> nessvector('Marie_Curie')
placeness     -0.463387
peopleness     0.354787
animalness     0.171099
conceptness   -0.320268
femaleness     0.257770
dtype: float64
>>> nessvector('Timbers')
placeness     -0.039665
peopleness     0.279271
animalness    -0.328952
conceptness    0.187153
femaleness    -0.097807
dtype: float64

>>> nessvector('Marie_Curie').round(2)
placeness     -0.46
peopleness     0.35
animalness     0.17
conceptness   -0.32
femaleness     0.26
dtype: float64

Now try to find the answer to the original question... it's hard.

>>> WV.most_similar(
...     'French France woman famous scientist chemistry Nobel_Prize radiation physics name person human'.split(),
...     negative='man man man man school ecole place country'.split())
...
[('Pierre_Curie', 0.48349958658218384),
 ('Henri_Becquerel', 0.47997117042541504),
 ('Otto_Warburg', 0.4735907316207886),
 ('blackbody_radiation', 0.47254103422164917),
 ('Nobelist', 0.46358683705329895),
 ('Kary_Mullis', 0.4630542993545532),
 ('Seoul_Soongsil_University', 0.461331844329834),
 ('George_Gamow', 0.45909202098846436),
 ('Nobel_Chemistry', 0.45735475420951843),
 ('Alivisatos', 0.45495474338531494)]
>>> WV.most_similar(
...     'Pierre_Curie Nobel_Prize famous smart French physics woman women person name'.split(),
...     negative='man male male geography city Pierre prize'.split())
...
[('Madame_Curie', 0.441272497177124),
 ('Ada_Lovelace', 0.4309345483779907),
 ('economist_Franco_Modigliani', 0.42140281200408936),
 ('physicist_Niels_Bohr', 0.4198070168495178),
 ('Murray_Gell_Mann', 0.41829752922058105),
 ('George_Gamow', 0.4176127314567566),
 ('brilliant_mathematician', 0.41744932532310486),
 ('Bertha_von_Suttner', 0.4144267439842224),
 ('Norbert_Wiener', 0.41063863039016724),
 ('Charles_Babbage', 0.40797877311706543)]

TODO:
automate the search for synonyms with higher than 60% similarity, walking a shallow graph
"""
from collections import OrderedDict

import numpy as np
import pandas as pd
# import scann  # noqa

# from nessvec.hypervec import cosine_similarity, WordVectors
from nessvec.files import load_glove as load

###################################################
# Still need to create a class derived from gensim's Word2vec model instead of relying on word_vectors globals


def component_vector(w2v, words, num_dim=50):
    words = [w for w in words if w in w2v]
    vector = np.zeros(num_dim)
    for word in words:
        v = w2v[word]
        vector += v / len(words)
    return vector


COMPONENT_WORDS = OrderedDict([
    ('placeness', ('place places geography Geography geographic geographical geographical_location location '
                   + 'locale locations proximity').split()),
    ('peopleness', 'person people human Humans homo_sapiens users team crowd individuals humankind men women'.split()),
    ('animalness', 'animal animals mammal carnivore animals Animal animal_welfare dog pet cats ani_mal'.split()),
    ('conceptness', 'concept concepts idea'.split()),
    ('femaleness', 'female Female females woman girl lady'.split()),
    ('maleness', 'male males man masculine macho boy dude gentleman beard mustache'.split()),
])


# wv = load_glove(filepath=
#     os.path.join(os.path.expanduser('~'), 'nessvec-data', 'glove.6B.50d.txt'))
# wv = load_glove(size=6, num_dim=50)
# wv = {}

def components_from_words(w2v, component_words=COMPONENT_WORDS):
    if not isinstance(component_words, (dict, OrderedDict)):
        wordlists = [tuple(w.split()) for w in component_words]
        component_words = dict((wl[0] + 'ness', wl) for wl in wordlists)
    return pd.DataFrame([
        component_vector(w2v, words) for (c, words) in component_words.items()],
        index=list(component_words.keys()))


def cosine_similarities(w2v, target, components=None):
    """ efficienty compute cosine similarity to list of vectors using numpy dot product """
    if components is None:
        components = components_from_words(w2v, COMPONENT_WORDS)
    components = np.array([w2v[c] if isinstance(c, str) else c for c in components if c in w2v])
    target = (w2v[target] if isinstance(target, str) else target).reshape(1, None)
    target /= np.linalg.norm(target)
    norms = np.linalg.norm(components, axis=1).reshape(None, 1)
    norms = norms.dot(np.ones((1, target.shape[1])))
    components /= norms
    return target.dot(components.T)


def nessvector(w2v, target, components):
    target = w2v[target] if isinstance(target, str) else target
    vector = word_vectors.cosine_similarities(target, components.values)
    return pd.Series((vector - vector.mean()) / .15, index=components.index)


class NessVec():
    def __init__(self, dim=50, size=6, component_words=COMPONENT_WORDS):
        self.dim = dim
        self.size = size
        self.w2v = IndexedVectors(load(dim=self.dim, size=self.size))
        self.reset_components(component_words)
        super().__init__()

    def component_vector(self, words):
        words = [w for w in words if w in self.w2v]
        vector = np.zeros(self.dim)
        for word in words:
            v = self.w2v[word]
            vector += v / len(words)
        return vector

    def reset_components(self, component_words=None):
        self.component_words = component_words or self.component_words
        if component_words is None:
            self.components = components_from_words(self.w2v, COMPONENT_WORDS)
        else:
            self.component_words = component_words
            self.components = components_from_words(self.w2v, component_words=component_words)

    def nessvector(self, target, components=None):
        self.components = components or self.components
        target = self.w2v[target] if isinstance(target, str) else target
        vector = self.cosine_similarities(target, self.components.values)
        return pd.Series((vector - vector.mean()) / .15, index=components.index)

    def cosine_similarities(self, target, components=None):
        """ efficiently compute cosine similarity to list of vectors using numpy dot product """
        if components is None:
            components = self.components
        # components = np.array([w2v[c] if isinstance(c, str) else c for c in components if c in w2v])
        target = (self.w2v[target] if isinstance(target, str) else target).reshape(1, None)
        target /= np.linalg.norm(target)
        norms = np.linalg.norm(components, axis=1).reshape(None, 1)
        norms = norms.dot(np.ones((1, target.shape[1])))
        components /= norms
        return target.dot(components.T)


# functions that should be part of a WordVector or KeyedVectors class
#########################################################################


def nessvector_marie_curie(num_dim):
    global word_vectors  # so the indexing doesn't have to be done again
    word_vectors['Marie_Curie']

    word_vectors['place'].std()
    word_vectors['place'].min()
    word_vectors['place'].max()

    word_vectors.most_similar('place')
    word_vectors.most_similar('location')
    word_vectors.most_similar('geography')

    placeness = np.zeros(num_dim)
    for word in COMPONENT_WORDS['placeness']:
        v = word_vectors[word]
        print(v.min(), v.max())
        placeness += v
    placeness /= 9.

    word_vectors.cosine_similarities(placeness,
                                     [word_vectors[word] for word in
                                      'place geography location address position'.split()])

    word_vectors.most_similar('animal')

    animalness = np.zeros(num_dim)

    animalness = np.zeros(num_dim)
    for word in 'animal mammal carnivore animals Animal animal_welfare dog pet cats ani_mal'.split():
        v = word_vectors[word]
        print(v.min(), v.max())
        animalness += v / 10.
    word_vectors.similar_by_vector(animalness)

    word_vectors.most_similar('people')
    word_vectors.most_similar('humans')

    peopleness = np.zeros(num_dim)
    for word in 'human Humans homo_sapiens peole people individuals humankind people men women'.split():
        v = word_vectors[word]
        print(v.min(), v.max())
        peopleness += v / 10.

    word_vectors.similar_by_vector(peopleness)
    word_vectors.similar_by_vector(animalness)
    word_vectors.similar_by_vector(placeness)

    target = word_vectors['Marie_Curie']
    word_vectors.cosine_similarities(target, [peopleness, animalness, placeness])

    word_vectors.most_similar('concept')

    conceptness = np.zeros(num_dim)
    for word in 'concept concepts idea'.split():
        v = word_vectors[word]
        print(v.min(), v.max())
        conceptness += v / 3.

    target = word_vectors['Marie_Curie']
    word_vectors.cosine_similarities(target, [peopleness, animalness, placeness, conceptness])

    word_vectors.most_similar('female')
    word_vectors.most_similar('woman')

    femaleness = np.zeros(num_dim)
    for word in 'female Female females femal woman girl lady'.split():
        v = word_vectors[word]
        femaleness += v / 7.

    word_vectors.similar_by_vector(conceptness)
    word_vectors.similar_by_vector(femaleness)

    target = word_vectors['Marie_Curie']
    mc_nessvector = word_vectors.cosine_similarities(
        target,
        [peopleness, animalness, placeness, conceptness, femaleness])
    return mc_nessvector


def semantic_search():
    global word_vectors  # so the indexing doesn't have to be done again
    word_vectors.most_similar(
        'French France woman famous scientist chemistry Nobel_Prize radiation physics name person human'.split(),
        negative='man man man man school ecole place country'.split())
    # [('Pierre_Curie', 0.48349958658218384),
    #  ('Henri_Becquerel', 0.47997117042541504),
    #  ('Otto_Warburg', 0.4735907316207886),
    #  ('blackbody_radiation', 0.47254103422164917),
    #  ('Nobelist', 0.46358683705329895),
    #  ('Kary_Mullis', 0.4630542993545532),
    #  ('Seoul_Soongsil_University', 0.461331844329834),
    #  ('George_Gamow', 0.45909202098846436),
    #  ('Nobel_Chemistry', 0.45735475420951843),
    #  ('Alivisatos', 0.45495474338531494)]
    word_vectors.most_similar(
        'Pierre_Curie Nobel_Prize famous smart French physics woman women person name'.split(),
        negative='man male male geography city Pierre prize'.split())


if __name__ == '__main__':
    nv = NessVecs()
    print(cosine_similarity(nv.w2v['seattle'], nv.w2v['portland']))
