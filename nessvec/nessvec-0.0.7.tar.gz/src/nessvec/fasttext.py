""" Load FastText or GloVe vectors from files into Dask dataframes

TODO: rename module to load_dask or dd or move load_glove to glove.load_dask

References

* Parquet file format for Dask: https://coiled.io/blog/parquet-file-column-pruning-predicate-pushdown/
* Dask tutorial: https://pythondata.com/dask-large-csv-python/
* Loaders and academic papers for embeddings: https://github.com/Hironsan/awesome-embedding-models
* Stanford GloVe vectors: https://nlp.stanford.edu/projects/glove/
* 400k 300d GloVe vectors: https://nlp.stanford.edu/data/glove.6B.zip
* FastText 1M 300d vectors loaded here: https://fasttext.cc/docs/en/english-vectors.html
* dataset package simple ORM sql: https://dataset.readthedocs.io/en/latest/
* word2vec c code: https://github.com/dav/word2vec/tree/master/data
* SOTA USE in 2018 was Elmo: https://medium.com/huggingface/universal-word-sentence-embeddings-ce48ddc8fc3a
"""
from csv import QUOTE_MINIMAL     # 0 # noqa
from csv import QUOTE_ALL         # 1 # noqa
from csv import QUOTE_NONNUMERIC  # 2 # noqa
from csv import QUOTE_NONE        # 3 # noqa
import dask.dataframe as dd
import datatable as dt
from files import vec_to_hdf5
import h5py
from nessvec.util import cosine_similarity
import numpy as np
import pandas as pd
from pathlib import Path
# import pynndescent as pynn
import pyarrow as pa
import pyarrow.parquet as pq
import sys
# from urllib.request import urlretrieve


DATA_DIR = Path('~/nessvec-data').expanduser().resolve().absolute()
STANFORD_GLOVE_PATH = DATA_DIR / 'glove.6B.300d.txt'
WIKINEWS_FASTTEXT_PATH = DATA_DIR / 'wiki-news-300d-1M.vec'


def load_glove(subword=False, filepath=STANFORD_GLOVE_PATH,
               skiprows=0, quoting=QUOTE_NONE, sep=' ', header=None,
               dtype={0: str}, **kwargs):
    """ Load Stanford GloVe vectors into dask.dataframe """
    filepath = str(filepath)
    ddf = dd.read_csv(
        filepath,
        header=header,
        skiprows=skiprows,
        dtype=dtype,
        quoting=quoting,
        sep=sep)
    # set_index doesn't work in a dask.dataframe
    # and parquet can't store strings in index
    tokens = np.array([str(x) for x in ddf[0]])
    vocab = dict(zip(tokens, range(len(tokens))))
    ddf = ddf[ddf.columns[1:]]
    ddf.columns = [str(c) for c in ddf.columns]
    return ddf, vocab


def load_fasttext_vec(subword=False, filepath=WIKINEWS_FASTTEXT_PATH,
                      skiprows=1, quoting=QUOTE_NONE, sep=' ', header=None, dtype={0: str}, **kwargs):
    """ Load fasttext vectors from local file into dask.dataframe

    Pretrained models by Facebook (2017):

    - [wiki-news-300d-1M.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M.vec.zip):
        1 million word vectors trained on Wikipedia 2017, UMBC webbase corpus and statmt.org news dataset (16B tokens).
    - [wiki-news-300d-1M-subword.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip):
        1 million word vectors trained with subword infomation on Wikipedia 2017, UMBC webbase corpus and statmt.org news dataset (16B tokens).
    - [crawl-300d-2M.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip):
        2 million word vectors trained on Common Crawl (600B tokens).
    - [crawl-300d-2M-subword.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M-subword.zip):
        2 million word vectors trained with subword information on Common Crawl (600B tokens).
    """

    # num_vecs, num_dim = WIKINEWS_GLOVE_PATH.open().readline().split()[:2]
    ddf = dd.read_csv(
        str(filepath),
        header=header,
        skiprows=skiprows,
        dtype=dtype,
        quoting=quoting,
        sep=sep,
        **kwargs
    )
    # set_index doesn't work in a dask.dataframe
    tokens = np.array([str(x) for x in ddf[0]])
    vocab = pd.Series(dict(zip(tokens, range(len(tokens)))))
    ddf = ddf[ddf.columns[1:]]
    ddf.columns = [str(c) for c in ddf.columns]
    return ddf, vocab


def compute(obj):
    """ Eager evaluation of all dask.dataframe.Delayed objects in an iterable

    >>> compute(load_glove(ddf.shape))
    (400000, 300)
    """
    if hasattr(obj, 'compute') and callable(obj.compute):
        return obj.compute()
    elif hasattr(obj, '__iter__'):
        return type(obj)([compute(x) for x in obj])
    return obj


def csv_to_parquet(filepath=WIKINEWS_FASTTEXT_PATH,
                   skiprows=1, quoting=QUOTE_NONE, sep=' ',
                   header=None, dtype={0: str}, chunksize=10000, **kwargs):
    """
    References:
        - https://www.mikulskibartosz.name/how-to-write-parquet-file-in-python/ """
    filepath = str(filepath)
    chunks = pd.read_csv(
        str(filepath),
        skiprows=skiprows,
        quoting=quoting,
        sep=sep,
        header=header,
        dtype=dtype,
        chunksize=chunksize,
        **kwargs)
    filepath += '.parquet'
    batches = (pa.RecordBatch.from_pandas(c) for c in chunks)  # names=schema
    table = pa.Table.from_batches(batches)
    pq.write_table(table, filepath)
    return filepath


def create_str_dataset(h5py_file, data, name='strings'):
    data = np.array(data, dtype=object)
    # # This fails to create extendable (chunked) dataset that can be resized
    # string_dt = h5py.special_dtype(vlen=str)
    # dset = h5py_file.create_dataset(name, data=data, dtype=string_dt)
    dset = h5py_file.create_dataset(
        name,
        shape=data.shape,
        maxshape=(None,),
        chunks=data.shape,
        dtype=data.dtype)
    return dset


def load_hdf5(filepath=str(WIKINEWS_FASTTEXT_PATH) + '.hdf5', encoding='utf8'):
    hdf5_file = h5py.File(filepath, 'r')
    vecs = hdf5_file['vecs']
    vocab = hdf5_file['vocab']
    vocab = pd.Series(data=range(len(vecs)), index=(s.decode(encoding) for s in vocab))
    if len(vocab) != len(vecs):
        print(f'vocab len = {len(vocab)} but vecs len = {len(vecs)}')
    # for s in hdf5_file['vocab']:
    #     try:
    #         vocab += [s.decode('utf8')]
    #     except UnicodeDecodeError:
    #         vocab += [s]
    #         print(vocab[max(-5, -len(vocab)):])
    return vecs, vocab

    # if not filepath_hdf.is_file():
    #     with h5py.File(str(filepath_hdf), 'w') as f:
    #         f.create_dataset(name, data=ddf.values)
    #         f.create_dataset(f'{name}_index', data=np.arange(num_vecs))
    #         # f.create_dataset(f'{name}_columns', data=np.array([f'x{i}' for i in np.arange(num_dims)]))
    # # TODO: THIS WORKS FAST!!!
    # h5file = h5py.File(str(filepath_hdf), 'r')
    # # f = h5py.File('fasttext.hdf'), 'r')
    # vecs.head()
    # return vecs


def read_parquet_dataframe(filepath=str(WIKINEWS_FASTTEXT_PATH) + '.parquet', kind='pandas'):
    """ Load a parquet file into a pandas or dask DataFrame

    WARNING:
        Requires 2.5 GB minimum to load 1M 300d 32bit vectors
        Uses a peak of 5.5 GB during the reading/indexing of the parquet file
    """

    filepath = str(filepath)
    if kind == 'pandas':
        table = pq.read_table(filepath)
        df = table.to_pandas()
        return df.set_index(0)
    else:  # 'dask'
        # Dask takes 1+ seconds to find a row by word and can't find it at all by rownum
        ddf = dd.read_parquet('/home/hobs/nessvec-data/wiki-news-300d-1M.vec.parquet')
        ddf.columns = [str(i) for i in range(301)]
        ddf.index = ddf['0']
        del ddf['0']
        return ddf


"""
TODO: Create H5DataFrame:

class H5DataFrame(pd.DataFrame):
    def __init__(self, h5file, name, *args, **kwargs):
        # kwargs['data'] = h5file[name]
        kwargs['index'] = pd.Series()
        return super().__init__(*args, **kwargs)
"""


class Index(pd.Series):
    def __init__(self, data, index=None):
        if index is None:
            index = range(len(data))
        self.data = data
        super().__init__(data=range(len(index)), index=index)

    def __getitem__(self, label):
        return self.data[super()[label]]


class H5DataFrame():
    def __init__(self, h5file, name, *args, **kwargs):
        # kwargs['data'] = h5file[name]
        self.data = h5file[name]
        self.columns = pd.Series(h5file[f'{name}_columns'])
        self.index = pd.Series(h5file[f'{name}_index'])
        self.shape = len(self.index), len(self.columns)
        self.reverse_columns = pd.Series(
            range(self.shape[1]), index=self.columns.values)
        self.reverse_index = pd.Series(
            range(self.shape[0]), index=self.index.values)
        self.loc = Index(data=self.data, index=self.index)
        self.iloc = Index(data=self.data)

    def __getitem__(self, label):
        return self.data[self.reverse_columns[label]]


def parse_argv(argv=sys.argv):
    name = 'fasttext'
    filepath = WIKINEWS_FASTTEXT_PATH
    if len(argv) > 1:
        name = str(sys.argv[1]).lower().lstrip('-')
    if name not in ('glove', 'fasttext'):
        ans = str(input(f'Load and index {filepath} vectors? (y/n)'))
        if ans.lower()[0].strip() != 'y':
            name = 'fasttext'
    filepath = DATA_DIR / name
    return filepath


def csv_to_datatable(
        filepath=Path('~/nessvec-data/glove.6B.50d.txt').expanduser(),
        sep=' ',
        header=None,
        skiprows=1,
        **kwargs):
    """ FIXME: fails on quotes in fasttext.vec format! -- Read a CSV file into a datatable Frame object.

    DEPRECATED!!! The datatable module is no longer maintained!!! Use Dask with parquet and hdf files

    [Pandas operations in datatable](https://datatable.readthedocs.io/en/latest/manual/comparison_with_pandas.html)
    """

    table = dt.fread(str(filepath),
                     sep=sep,
                     header=header,
                     skip_to_line=skiprows,
                     **kwargs)
    vocab = dict(
        zip((x[0] for x in table['C0'].to_numpy()), range(table.shape[0]))
    )
    table[:, 0]
    table.names = [str(i) for i in range(table.shape[1])]
    return table, vocab


def csv_to_dataframe(
        filepath=Path('~/nessvec-data/glove.6B.50d.txt').expanduser(),
        sep=' ',
        header=None,
        skiprows=1,
        **kwargs):
    """ Read a CSV file into a Pandas DataFrame object

    [Pandas operations in datatable](https://datatable.readthedocs.io/en/latest/manual/comparison_with_pandas.html)

    """
    table = pd.read_csv(str(filepath),
                        sep=sep,
                        header=header,
                        skiprows=skiprows,
                        quoting=QUOTE_NONE,
                        **kwargs)
    vocab = dict(
        zip((x[0] for x in table['C0'].to_numpy()), range(table.shape[0]))
    )
    table[:, 0]
    table.names = [str(i) for i in range(table.shape[1])]
    return table, vocab


def test_cosine_similarity(filepath=Path('~/nessvec-data/glove.6B.50d.txt').expanduser(), **kwargs):
    """ FIXME: cosine_similarity on 50D glove vector math doesn't work

    1. Try different vectors (100D, 300D, FastText, Word2Vec)
    2. Verify cosine_similarity works similarly to gensim
    3. Find online examples

    >>> red = table[vocab['red'], :].to_numpy()[0]
    >>> hot = table[vocab['hot'], :].to_numpy()[0]
    >>> blue = table[vocab['blue'], :].to_numpy()[0]
    >>> from nessvec.util import cosine_similarity
    >>> cosine_similarity(red, hot)
    0.6062780518370962
    >>> cosine_similarity(red, blue)
    0.8901658048402964
    >>> cosine_similarity(blue, hot)
    0.5972493232772841
    >>> king = table[vocab['king'], :].to_numpy()[0]
    >>> queen = table[vocab['queen'], :].to_numpy()[0]
    >>> woman = table[vocab['woman'], :].to_numpy()[0]
    >>> man = table[vocab['man'], :].to_numpy()[0]
    >>> total = queen - woman + man
    >>> cosine_similarity(queen, total)
    0.8774592271884951
    >>> cosine_similarity(king, total)
    0.8588839182356068
    >>> sum((king - total)**2)
    8.06060602717927
    >>> sum((queen - total)**2)
    6.773649515923383
    >>> total_queen = king - man + woman
    >>> cosine_similarity(queen, total_queen)
    0.8609...
    >>> cosine_similarity(king, total_queen)
    0.8859...
    """
    similarities = {}
    table, vocab = csv_to_datatable(filepath)
    red = table[vocab['red'], :].to_numpy()[0]
    hot = table[vocab['hot'], :].to_numpy()[0]
    blue = table[vocab['blue'], :].to_numpy()[0]
    cool = table[vocab['cool'], :].to_numpy()[0]
    similarities['red.hot'] = cosine_similarity(red, hot)
    similarities['red.blue'] = cosine_similarity(red, blue)
    similarities['blue.hot'] = cosine_similarity(blue, hot)
    similarities['blue.cool'] = cosine_similarity(blue, cool)
    similarities['red_hot_score'] = (similarities['blue.cool'] + similarities['red.hot']) / 2

    king = table[vocab['king'], :].to_numpy()[0]
    queen = table[vocab['queen'], :].to_numpy()[0]
    woman = table[vocab['woman'], :].to_numpy()[0]
    man = table[vocab['man'], :].to_numpy()[0]
    total_king = queen - woman + man
    total_queen = king - man + woman

    similarities['total_king.king'] = cosine_similarity(total_king, king)
    similarities['total_king.queen'] = cosine_similarity(total_king, queen)
    similarities['total_queen.queen'] = cosine_similarity(total_queen, queen)
    similarities['total_queen.king'] = cosine_similarity(total_queen, king)

    similarities['king_queen_score'] = (similarities['total_king.king'] + similarities['total_queen.queen']) / 2
    similarities['score'] = (similarities['red_hot_score'] + similarities['king_queen_score']) / 2

    similarities['relative_score_king'] = (similarities['total_king.king'] - similarities['total_king.queen']) / similarities['total_king.queen']
    similarities['relative_score_queen'] = (similarities['total_queen.queen'] - similarities['total_queen.king']) / similarities['total_queen.king']

    similarities['score'] = (similarities['relative_score_king'] + similarities['relative_score_queen']) / 2

    # assert cosine_similarity(queen, total_king) < .95 * cosine_similarity(king, total_king)
    euclidian_distance = 1 - (sum((king - total_king)**2) ** .5) / (sum((queen - total_king)**2) ** .5)
    similarities['euclidian_distance_ratio_score_king_queen'] = euclidian_distance
    return similarities


def compare_word_vector_models():
    all_scores = []
    for filepath in [
            Path('~/nessvec-data/glove.6B.50d.txt').expanduser(),
            Path('~/nessvec-data/glove.6B.100d.txt').expanduser(),
            Path('~/nessvec-data/glove.6B.300d.txt').expanduser(),
    ]:
        all_scores.append(test_cosine_similarity(filepath))
    return pd.DataFrame(all_scores)


class IndexedVectors(pd.Series):
    def __init__(data, index, **vocab):
        """ Create DataFrame with row lookup method similar to .iloc and .loc but within row() """


def main():
    """ TODO: vocab and ddf len mismatch:

    3 vectors do not have a vocab term entry for them:

    >>> num_vecs
    999994
    >>> ddf.shape
    (Delayed('int-5779cad2-bfdf-41d2-9cf4-0340c284fa3b'), 300)
    >>> ddf.shape[0].compute()
    999994
    >>> len(vocab)
    999990
    >>> max(vocab.values)
    999993
    """
    filepath = parse_argv()
    filepath_pq = Path(str(filepath) + '.parquet')
    filepath_hdf = Path(str(filepath) + '.hdf')
    filepath_dt = Path(str(filepath) + '.dt')
    if filepath_pq.is_file():
        ddf = dd.read_parquet(str(filepath_pq))
    elif filepath_hdf.is_file():
        ddf = dd.read_hdf(str(filepath_hdf))
    elif filepath_dt.is_file():
        ddf = dd.read_hdf(str(filepath_dt))
    elif 'fasttext' in filepath.lower():
        ddf, vocab = load_fasttext_vec(filepath)
    elif 'glove' in filepath.lower():
        ddf, vocab = load_glove(filepath)

    num_vecs = ddf.shape[0].compute()
    num_dims = ddf.shape[1]  # noqa

    ddf.head()
    return dict(ddf=ddf, shape=(num_vecs, num_dims))


if __name__ == '__main__':
    filepath = WIKINEWS_FASTTEXT_PATH
    filepath_hdf5 = str(filepath) + '.hdf5'
    if not Path(str(filepath) + '.hdf5').is_file():
        vec_to_hdf5(WIKINEWS_FASTTEXT_PATH)
    # d = load_hdf5(filepath_hdf5)
