import IPython.display
import numpy as np
from urllib.request import urlopen
from pathlib import Path


class Audio(IPython.display.Audio):

    def __init__(self, data=None, filename=None, url=None, embed=None, rate=None, autoplay=False, normalize=False):
        if not normalize and data is not None:
            data_array = np.asarray(data)
            # convert non-floating point data to floating point in interval [-1, 1]
            if np.issubdtype(data_array.dtype, np.signedinteger):
                data = 1 / 2**(8*data_array.dtype.itemsize-1) * data_array
            elif np.issubdtype(data_array.dtype, np.unsignedinteger):
                data = 1 / 2**(8*data_array.dtype.itemsize-1) * data_array - 1
        try:
            super().__init__(data=data, filename=filename, url=url, embed=embed, rate=rate, autoplay=autoplay, normalize=normalize)
        except TypeError:
            if not normalize and data is not None:
                s = list(data.shape)
                s[-1] = 1
                data = np.append(data, np.ones(s), axis=-1)
            super().__init__(data=data, filename=filename, url=url, embed=embed, rate=rate, autoplay=autoplay)        


def download_file(url, file_path, verbose=True, overwrite=False):
    p = Path(file_path)
    if not p.exists() or overwrite:
        if verbose:
            print(f'Downloading {p}')
        p.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(url) as r:
            p.write_bytes(r.read())
