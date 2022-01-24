import logging
from deepdog.meta import __version__
from deepdog.bayes_run import BayesRun


def get_version():
	return __version__


__all__ = ["get_version", "BayesRun"]


logging.getLogger(__name__).addHandler(logging.NullHandler())
