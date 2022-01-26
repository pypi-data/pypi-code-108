import os
import json
import tarfile
import hashlib
from io import BytesIO


def get_model_version(obj, blength=4):
    """
    Calculate version of model archive
    :param obj: fname path to model archive or BufferedIOBase
    :param blength: bytelength of model version (4)
    :return:
    """
    try:
        hash_md5 = hashlib.md5()
        if isinstance(obj, BytesIO):
            for chunk in iter(lambda: obj.read(4096), b""):
                hash_md5.update(chunk)
        else:
            with open(obj, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        return int.from_bytes(hash_md5.digest()[:blength], byteorder='little', signed=False)
    except FileNotFoundError:
        return -1


def check_model_version(fname=None, version=None, fileobj=None, blength=4):
    """
    Check model version is correct
    :param fname: path to model archive, or filelike obj
    :param fileobj: BytesIO if model in memory
    :param blength: bytelength of model version (4)
    :return: Version number of file if correct, False if not correct and None if not a known file type
    """
    try:
        fileobj = fileobj or fname
        version = version or int(fname.rsplit(".", 3)[-3])
        true_version = get_model_version(fileobj, blength)
        return true_version if version == true_version else False
    except Exception:
        return False

def saved_model_model_meta_filename(saved_model_dir):
    return os.path.join(saved_model_dir, "assets.extra", "criterion_model_meta.json")


def package_saved_model(saved_model_dir, name="saved_model", output=None, model_meta=None):
    """
    Utility function to package saved model to archive
    :param saved_model_dir: path to saved model directory
    :param name: name of model
    :param output: forced output path use given name in place of name with model version
    :return: archive path
    """

    if model_meta is not None:
        model_meta_path = saved_model_model_meta_filename(saved_model_dir)
        os.makedirs(os.path.dirname(model_meta_path), exist_ok=True)
        with open(model_meta_path, "w") as fp:
            json.dump(model_meta, fp)

    # Package
    saved_model_tar = output or os.path.join(saved_model_dir + '.tar.gz')
    with tarfile.open(saved_model_tar, "w:gz") as tar:
        tar.add(saved_model_dir, arcname="saved_model")

    # Rename
    if output is None:
        root_dir = os.path.dirname(saved_model_dir)
        output = os.path.join(root_dir, f"{name}.{get_model_version(saved_model_tar)}.tar.gz")
        os.rename(saved_model_tar, output)

    return output
