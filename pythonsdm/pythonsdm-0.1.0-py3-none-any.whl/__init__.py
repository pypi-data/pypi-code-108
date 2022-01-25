from fire import Fire
from pythonsdm.sdm import sdm_train, sdm_test


def train():
    Fire(sdm_train)


def test():
    Fire(sdm_test)
