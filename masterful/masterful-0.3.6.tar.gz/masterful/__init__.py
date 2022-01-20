# Masterful only supports tensorflow 2.4.0+
def _check_tensorflow_version():
  from packaging import version
  try:
    import tensorflow as tf
    assert version.parse(tf.__version__) >= version.parse(
        '2.4.0'
    ), "Masterful only supports Tensorflow versions 2.4.0 and greater."
  except ImportError:
    print(
        "Masterful requires Tensorflow 2.4+. Please install Tensorflow before installing Masterful."
    )
    exit()


_check_tensorflow_version()

from masterful.version import __version__
from masterful.utils.register import register