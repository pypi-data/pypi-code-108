from time import perf_counter

import pytest

from niota import signature, Niota


@pytest.fixture
def key_pair_fixture():
    return signature.generate_key_pair()


@pytest.fixture
def message_data_fixture():
    return {
        'raw_cid': 'bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku',
        'ida_cid': 'bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku',
        'ida_mid': 'c7dfa6e5-346d-4b4d-a663-a421e7f9171f',
        'ida_sha256sum': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'metadata_cid': 'bafkreidgkmzpzvot7a5r2iy44tmcojuvoyjgbwi5udldfisbvn4lnfrmoq',
        'service_message': 'Create test data',
    }


def test_create_multiple_messages(key_pair_fixture, message_data_fixture):
    private_key, public_key = key_pair_fixture

    niota = Niota(
        private_key=private_key, public_key=public_key,
    )

    for _ in range(10):
        start = perf_counter()
        niota.create_message(**message_data_fixture)
        end = perf_counter()
        print(f'Elapsed time: {end - start}')
