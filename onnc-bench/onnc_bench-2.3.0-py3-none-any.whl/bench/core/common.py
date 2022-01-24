import tempfile
import threading
import os


def get_class_name(model):
    c = model.__class__.__mro__[0]
    name = c.__module__ + "." + c.__name__
    return name


def get_temp_base():
    tid = str(threading.get_ident())
    return os.path.join(tempfile._get_default_tempdir(),
                        'onnc-bench', tid)


def get_tmp_path():
    temp_base = get_temp_base()

    if not os.path.exists(temp_base):
        os.makedirs(temp_base, exist_ok=True)
    return os.path.join(temp_base,
                        next(tempfile._get_candidate_names()))


