import json
import pytest
from pytest_mock import MockerFixture

from niota import chrysalis, signature, Niota


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


@pytest.mark.integration
def test_create_message_compatible(mocker: MockerFixture, key_pair_fixture, message_data_fixture):
    private_key, public_key = key_pair_fixture

    # Patch timestamp to make message content consistent
    mocker.patch('niota.chrysalis.IotaClient._get_current_timestamp', return_value=1)
    mocker.patch('niota.niota.Niota.get_current_timestamp', return_value=1)

    # Create message using legacy chrysalis.py client
    legacy_client = chrysalis.IotaClient(private_key, public_key)
    legacy_message_id, legacy_index = legacy_client.create_message(**message_data_fixture)
    legacy_data_str = legacy_client.get_message_data(legacy_message_id)
    legacy_data = json.loads(legacy_data_str)['data']
    legacy_client.verify_message_data(legacy_data_str)

    # Create message using new niota.py client
    niota = Niota(private_key=private_key, public_key=public_key)
    niota_message_id, niota_index = niota.create_message(**message_data_fixture)
    niota_data_str = legacy_client.get_message_data(niota_message_id)
    niota_data = json.loads(niota_data_str)['data']
    legacy_client.verify_message_data(niota_data_str)

    assert legacy_data == niota_data
    assert legacy_index == niota_index
