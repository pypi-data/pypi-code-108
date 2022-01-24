# indexers.py
from files import load_hdf5
import numpy as np
import pynndescent as pynn  # conda install -c conda-forge pynndescent
import pandas as pd         # conda install -c conda-forge pandas
import psutil               # conda install -c anaconda psutil
import time


class Index(pynn.NNDescent):
    def query(self, query_data, *args, **kwargs):
        return super().query(np.array(query_data).reshape((-1, self.dim)), *args, **kwargs)


ANALOGY_FILEPATH = 'https://gitlab.com/tangibleai/word-vector-benchmarks/-/raw/main/word-analogy/monolingual/en/sat.csv'


def load_analogies(filepath=ANALOGY_FILEPATH):
    # Load an analogy dataset
    df_analogy = pd.read_csv(filepath, index_col=0)
    df_6_analogies = df_analogy.sample(6)
    print(df_6_analogies)

    for i, row in df_6_analogies.iterrows():
        print(f'"{row.word1.title()}" is to "{row.word2}" as "{row.word3}" is to "{row.target}"')

    # filter out the rows with these words
    # ...['unfetter', 'unfrock', 'abash']
    is_valid = []
    for analogy_words in df_analogy.values[:, 1:]:
        is_valid.append(True)
        try:
            vocab[analogy_words]
        except KeyError:
            print(f"Can't find some of these words: {analogy_words}")
            is_valid[-1] = False

    df_analogy = df_analogy[is_valid].copy()
    for c in df_analogy.columns[1:]:
        df_analogy[c + '_id'] = vocab[df_analogy[c]]

    return df_analogy
    # "Sink" is to "plumber" as "meat" is to "butcher"
    # "Plug" is to "insert" as "clamp" is to "grip"
    # "Noisy" is to "uproar" as "tanned" is to "leather"
    # "Ceremony" is to "sermon" as "agenda" is to "advertisement"
    # "Tale" is to "story" as "week" is to "year"
    #   ^ SEEMS INCORRECT TO ME
    # "Antiseptic" is to "germs" as "illness" is to "fever"

    # TODO: search the analogies for NLP/language/linguistics/story/text/writing/computer-related analogies
    #       subject = vocab['NLP'] + vocab['language'] + vocab['English'] + vocab['computer'] + vocab['AI']
    df_analogy.sample(6)
    # ...

    index.query(np.array([vecs[vocab['king']]]))[0][0]
    # np.ndarray([2407, 7697, 6406, 1067, 9517, 7610, 600459, 5409, 854338, 5094])

    vocab.iloc[index.query(np.array([vecs[vocab['king']] - vecs[vocab['man']] + vecs[vocab['woman']]]))[0][0]]
    # king               2407
    # queen              6406
    # kings              7697
    # monarch            9517
    # princess          11491
    # king-            600459
    # King               1067
    # prince             7610
    # queen-consort    623878
    # queendom         836526
    # dtype: int64

    neighbors = index.query(np.array([vecs[vocab['king']] - vecs[vocab['man']] + vecs[vocab['woman']]]))
    neighbors = pd.DataFrame(
        zip(
            neighbors[0][0],
            neighbors[1][0],
            vocab.iloc[neighbors[0][0]].index.values
        ),
        columns='word_id distance word'.split())


def time_and_memory(resources_t0=0):
    resources = {}
    resources.update(dict(psutil.virtual_memory()._asdict()))
    resources.update({'wall_time': time.time()})
    return pd.Series(resources) - resources_t0


def index_vectors(vecs):
    # keep track of the time and memory used for each big task

    resources_start = time_and_memory()
    index = Index(vecs)
    index.prepare()
    resources['pynndescent_index'] = time_and_memory(resources_start)

    resources_start = time_and_memory()
    index.query(vecs[vocab['king']].reshape((-1, index.dim)))
    resources['pynn_query'] = time_and_memory(resources_start)

    return index


if __name__ == '__main__':
    resources = pd.DataFrame()

    # Load the 1Mx300 FastText vectors trained on wikipedia
    resources_start = time_and_memory()
    vecs, vocab = load_hdf5()
    resources['load_hdf5'] = time_and_memory(resources_start)

    index = index_vectors(vecs)

    df_analogies = load_analogies()
