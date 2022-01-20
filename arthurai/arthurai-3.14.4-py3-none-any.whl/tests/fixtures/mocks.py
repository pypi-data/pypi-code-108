import logging

import pytest

from arthurai import ArthurAI


BASE_URL = "http://mock"
ACCESS_KEY = "FAKE_ACCESS_KEY"
USER_ACCESS_KEY = "USER_ACCESS_KEY"


@pytest.fixture(scope="class")
def client():
    logging.info("Creating mock ArthurAI Client")

    access_key = "FAKE_ACCESS_KEY"

    config = {
        'access_key': access_key,
        'url': BASE_URL,
        'offline': True
    }
    return ArthurAI(config)
