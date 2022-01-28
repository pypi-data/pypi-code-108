# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""NIST SPH audio-file format"""
from pathlib import Path

import numpy

from .._data_obj import NDVar, Scalar, UTS
from .._types import PathArg
from .._utils import ui


def load_sphere(
        filename: PathArg = None,
        name: str = None,
) -> NDVar:
    """Load NIST SPH audio-files (uses `sphfile <https://pypi.org/project/sphfile/>`_

    Parameters
    ----------
    filename
        Filename of the file. If not filename is specified, a file dialog is
        shown to select one.
    name
        NDVar name (default is the file name).
    """
    try:
        import sphfile
    except ImportError:
        raise ImportError("The sphfile library needs to be installed; run:\n $ pip install sphfile")

    if filename is None:
        path = ui.ask_file("Load NIST SPH audio", "Select NIST SPH audio file to load as NDVar", [("NIST SPH audio-file", "*.WAV")])
        if not path:
            return
    else:
        path = Path(filename)
        if not path.suffix and not path.exists():
            path = path.with_suffix('.WAV')

    sphere_file = sphfile.SPHFile(path)
    time = UTS(0, 1. / sphere_file.format['sample_rate'], sphere_file.format['sample_count'])
    if name is None:
        name = path.name
    info = {'filename': str(path), **sphere_file.format}
    if sphere_file.content.ndim == 1:
        return NDVar(sphere_file.content, (time,), name, info)
    elif sphere_file.content.ndim == 2:
        chan = Scalar('channel', numpy.arange(sphere_file.content.shape[1]))
        return NDVar(sphere_file.content, (time, chan), name, info)
    else:
        raise NotImplementedError(f"Data with {sphere_file.content.ndim} dimensions")
