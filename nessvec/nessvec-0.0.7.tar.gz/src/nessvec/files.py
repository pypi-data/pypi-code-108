""" File Management module 

## Data sources

### Pre-trained FASTTEXT word vectors:

1. [wiki-news-300d-1M.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M.vec.zip):
  - 1M word vectors
  - Wikipedia 2017, UMBC webbase corpus and statmt.org news dataset (16B tokens)
2. [wiki-news-300d-1M-subword.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip):
  - 1M word vectors
  - trained on subwords from Wikipedia 2017 subwords, UMBC webbase corpus, and statmt.org news (16B tokens).
3. [crawl-300d-2M.vec.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip):
  - 2M word vectors
  - Common Crawl (600B tokens)
4. [crawl-300d-2M-subword.zip](https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M-subword.zip)
  - 2M word vectors
  - subwords from Common Crawl (600B tokens)
"""
from constants import DATA_DIR
from csv import QUOTE_MINIMAL     # 0 # noqa
from csv import QUOTE_ALL         # 1 # noqa
from csv import QUOTE_NONNUMERIC  # 2 # noqa
from csv import QUOTE_NONE        # 3 # noqa
import datatable as dt
import h5py
import logging
import numpy as np
import os
import pandas as pd
from pathlib import Path
# import pandas as pd
import re
from tqdm import tqdm
from urllib.request import urlretrieve
from zipfile import ZipFile

log = logging.getLogger(__name__)

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


FASTTEXT_URLS = [
    'https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M.vec.zip',
    'https://dl.fbaipublicfiles.com/fasttext/vectors-english/wiki-news-300d-1M-subword.vec.zip',
    'https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M.vec.zip',
    'https://dl.fbaipublicfiles.com/fasttext/vectors-english/crawl-300d-2M-subword.zip',
]


STANFORD_GLOVE_PATH = DATA_DIR / 'glove.6B.300d.txt'
WIKINEWS_FASTTEXT_PATH = DATA_DIR / 'wiki-news-300d-1M.vec'


def show_progress(block_num, block_size, total_size):
    pbar = show_progress.pbar

    if pbar is None:
        pbar = tqdm(total=total_size)
        pbar.start_t()
    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.moveto(downloaded)
    else:
        pbar.finish()
        show_progress.pbar = None


show_progress.pbar = None


def load_glove(dim=50, size=6, filepath=None):
    """ Download and return the specified GloVe word vectors dict from Stanford

    >>> wv = load_glove(dim=50, size=6)
    >>> len(wv)
    400000
    """
    dim = str(dim).lower().rstrip('d')
    filepath = Path(filepath or Path(DATA_DIR).joinpath(GLOVE_FILENAME_TEMPLATE.format(
        dim=dim, size=size)))
    zippath = Path(filepath).parent.joinpath(GLOVE_ZIP_FILENAME_TEMPLATE.format(size=size))
    # if filepath.lower()[-4:] == '.zip':
    #     filepath = unzip(filepath)

    if not filepath.is_file():
        log.warning(f'filepath: {filepath}')
        if not zippath.is_file():
            # log.debug(zippath)
            log.warning(f'zippath: {zippath}')
            zippath = download_glove(size=size)
        if not zippath:
            return None
        # log.info(zippath)
        filepaths = unzip_files(zippath)
        log.error(f'filepaths: {filepaths}')
        if filepath not in filepaths:
            filepaths = [fp for fp in filepaths if fp.endswith('d.txt')]
            if filepaths:
                filepath = filepaths[0]
            else:
                return None

    f = open(filepath, 'r')
    wv = {}
    for i, line in tqdm(enumerate(f)):
        splitLines = line.split()
        word = splitLines[0]
        embedding = np.array([float(value) for value in splitLines[1:]])
        wv[word] = embedding
    return wv


def ensure_path(path):
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve().absolute()


resolve = ensure_path


def unzip_files(zip_filepath, filename=None, data_dir=DATA_DIR):
    if isinstance(filename, str) and filename.lower().strip() not in ('all', '*', ''):
        filenames = [filename]
    zip_filepath = ensure_path(zip_filepath)
    with ZipFile(str(zip_filepath), 'r') as zipobj:
        if filenames is None:
            filenames = zipobj.namelist()
        for fn in filenames:
            zipobj.extract(str(fn), path=data_dir)
    dest_filepaths = [data_dir.joinpath(fn) for fn in filenames]
    return dest_filepaths


def unzip_glove(zip_filepath, filename=None, dim=None, size=None):
    """ Extract txt files from ZipFile and place them all in the dest_filepath or DATA_DIR """
    zip_filepath = Path(zip_filepath)
    sizematch = re.search(r'[.](\d{1,3})B[.]', str(zip_filepath))
    if sizematch:
        size = int(sizematch.groups()[0])
    if filename is None and (dim or size):
        filename = GLOVE_FILENAME_TEMPLATE.format(dim=(dim or 50), size=(size or 6))
    dest_filepaths = unzip_files(zip_filepath, filename=filename)

    return dest_filepaths


def download(url, data_dir=DATA_DIR, filepath=None, filename=None):
    """ Download a file from a url and put it in data_dir or filepath or DATA_DIR/filepath

    >>> download('https://nlp.stanford.edu/data/glove.6B.zip')

    """
    data_dir = ensure_path(data_dir)
    if not data_dir.is_dir():
        data_dir.mkdir()

    if not filepath:
        if not filename:
            filename = os.path.split(url)[-1]  # this separates url by '/' and takes the last part
        filepath = data_dir / filename
    filepath = ensure_path(filepath)

    if not filepath.is_file():
        urlretrieve(url, filepath, show_progress)
        # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko)"
        # headers = {'User-Agent': user_agent}

        # # using requests to download and open file
        # with requests.get(url, stream=True, headers=headers) as resp:
        #     with filepath.open('wb') as fout:
        #         for chunk in tqdm(resp.iter_content(chunk_size=8192)):
        #             fout.write(chunk)

    return filepath


# def load_ann_benchmark(name='glove-100-anglular'):
#     url = f"http://ann-benchmarks.com/{name}.hdf5"
#     filepath = DATA_DIR / f"{name}.hdf5"
#     if not filepath.is_file():
#         log.debug(f"Dataset {name} is not cached; downloading now ...")
#         urlretrieve(url, filepath, show_progress)
#     return h5py.File(filepath, "r")
    # return np.array(hdf5_file['train']), np.array(hdf5_file['test']), hdf5_file.attrs['distance']


def load_ann_benchmark(name='glove-100-angular'):
    url = f"http://ann-benchmarks.com/{name}.hdf5"
    filepath = DATA_DIR / f"{name}.hdf5"
    if not filepath.is_file():
        log.warning(f"Dataset {name} is not yet cached; downloading now ...")
        urlretrieve(url, filepath, show_progress)
    return h5py.File(filepath, "r")


def download_glove(size=6, url=None, dest_filepath=None):
    """ download and extract text file containig pairs of translated phrases

    Inputs:
        corpus (str): 6B | 42B | 84B | twitter.27B
        url (full url to the zip file containing a GloVe vector model)
    Returns:
        path_to_zipfile (str)
    """
    size = str(size).lower().strip()
    size = size.rstrip('b')
    if size.endswith('27'):
        size = 'twitter.27'
    url = url or GLOVE_URL_TEMPLATE.format(size=size)
    log.warning(url)

    return download(url=url)


def txt_to_datatable(
        filepath=Path('~/nessvec-data/glove.6B.50d.txt').expanduser(),
        sep=' ',
        header=None,
        skiprows=1,
        **kwargs):
    """ Load Stanford GlovVE .txt file into datatable.Table

    FIXME: fails on quotes in fasttext.vec format! -- Read a CSV file into a datatable Frame object.

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


def vec_to_hdf5(filepath=WIKINEWS_FASTTEXT_PATH,
                skiprows=1, quoting=QUOTE_NONE, sep=' ',
                encoding='utf8',
                header=None, chunksize=10000, **kwargs):
    """ Comvert FASTTEXT .vec file into chunked hdf5 file format for out-of-core processing

    References:
       - General algorithm for efficient hdf5 file creation using chunking of pd.read_csv(): https://stackoverflow.com/a/34533601/623735
    """
    num_vecs, num_dims = [int(i) for i in Path(filepath).open().readline().split()[:2]]
    log.info(f'Loading {num_vecs}x{num_dims} word vectors from {filepath}.')
    # vocab is read into RAM in its entirety to avoid truncation of the longer strings if read in chunks
    vocab = pd.read_csv(
        filepath,
        header=header,
        skiprows=skiprows,
        dtype={0: str},
        usecols=[0],
        quoting=quoting,
        sep=sep,
    )[0]
    vocab = vocab.str.encode('utf8').astype(bytes)
    vec_chunks = pd.read_csv(
        str(filepath),
        skiprows=skiprows,
        quoting=quoting,
        sep=sep,
        header=header,
        dtype=np.float32,
        usecols=range(1, num_dims + 1),
        # encoding='latin',
        chunksize=chunksize,
        **kwargs)

    filepath_hdf5 = str(filepath) + '.hdf5'

    with h5py.File(filepath_hdf5, 'w') as f:
        # Initialize a resizable dataset to hold the output
        dset_vecs = f.create_dataset(
            'vecs',
            shape=(num_vecs, num_dims),
            chunks=(chunksize, num_dims),
            dtype=np.float32)
        dset_vocab = f.create_dataset('vocab', data=vocab)  # noqa

        rownum = 0
        for vec_chunk in vec_chunks:
            dset_vecs[rownum:rownum + vec_chunk.shape[0]] = vec_chunk
            rownum += vec_chunk.shape[0]

    return filepath_hdf5


def load_hdf5(filepath=str(WIKINEWS_FASTTEXT_PATH) + '.hdf5', encoding='utf8'):
    hdf5_file = h5py.File(filepath, 'r')
    vecs = hdf5_file['vecs']
    vocab = hdf5_file['vocab']
    vocab = pd.Series(data=range(len(vecs)), index=(s.decode(encoding) for s in vocab))
    if len(vocab) != len(vecs):
        log.error(f'vocab len = {len(vocab)} but vecs len = {len(vecs)}')
    # for s in hdf5_file['vocab']:
    #     try:
    #         vocab += [s.decode('utf8')]
    #     except UnicodeDecodeError:
    #         vocab += [s]
    #         log.error(vocab[max(-5, -len(vocab)):])
    return vecs, vocab
