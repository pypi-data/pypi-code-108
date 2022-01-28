import h5py
import json


def set_metadata(h5_path, metadata):
    if not isinstance(metadata, str):
        metadata = json.dumps(metadata)
    with h5py.File(h5_path, mode='a') as f:
        f.attrs['metadata'] = metadata


def get_metadata(h5_path):
    with h5py.File(h5_path, mode='r') as f:
        if "metadata" in f.attrs:
            return json.loads(f.attrs['metadata'])
        else:
            return {}


def save_model(path, model, metadata):
    assert path.endswith(".h5")
    retval = model.save(path)
    set_metadata(path, metadata)
    return retval