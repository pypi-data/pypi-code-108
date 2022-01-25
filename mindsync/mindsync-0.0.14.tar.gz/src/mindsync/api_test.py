import pytest
from unittest.mock import patch, AsyncMock, create_autospec

from mindsync.api import AsyncApi, MindsyncApiError, DEFAULT_BASE_URL

from aiohttp import ClientResponse, ClientConnectionError


API_KEY = 'an-api-key'
USER_ID = 'an-user-id'
RESPONSE_RV = dict(result=dict(first_name='Elvis', last_name='Presley'))
RIG_ID = 'a-rig-id'
RENT_ID = 'a-rent-id'
API_VERSION = '1.0'


@pytest.fixture
def api_key():
    return API_KEY


@pytest.fixture
def sut(api_key):
    return AsyncApi(api_key)


@pytest.fixture
def resp_mock():
        mock = create_autospec(spec=ClientResponse, spec_set=True, instance=True)
        mock.json.return_value = RESPONSE_RV
        return mock


@pytest.fixture
def aiohttp_request_mock(resp_mock):
    with patch('aiohttp.request') as mock:
        mock.return_value.__aenter__.return_value = resp_mock
        yield mock


@pytest.mark.parametrize('user_id, url', [(None, f'{DEFAULT_BASE_URL}/api/1.0/users/client/profile'), 
                                          (USER_ID, f'{DEFAULT_BASE_URL}/api/1.0/users/profile/{USER_ID}')])
@pytest.mark.asyncio                                          
async def test_profile_must_do_proper_http_request(sut, user_id, url, api_key, aiohttp_request_mock):
    result = await sut.profile(user_id)

    assert RESPONSE_RV['result'] == result
    aiohttp_request_mock.assert_called_with(method='GET', url=url, 
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio                                          
async def test_profile_must_raise_if_request_fails(sut, aiohttp_request_mock):
    aiohttp_request_mock.side_effect = ClientConnectionError

    with pytest.raises(MindsyncApiError):
        await sut.profile()


@pytest.mark.asyncio                                          
async def test_profile_must_raise_if_result_is_malformed(sut, resp_mock, aiohttp_request_mock):
    resp_mock.json.return_value = dict()

    with pytest.raises(MindsyncApiError):
        await sut.profile()


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_args', [(dict(first_name='Jim', last_name='Carrey', phone='1234567'), 
                                            dict(lastName='Carrey', firstName='Jim',  phone='1234567'))])
async def test_set_profile_must_do_proper_http_request(sut, args, expected_args, api_key, 
                                                         aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.set_profile(**args)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='PUT', 
                                            url=f'{DEFAULT_BASE_URL}/api/1.0/users/client/profile', 
                                            json=expected_args,
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_url', [(dict(my=True), f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rigs/my'), 
                                                (dict(my=False), f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rigs')])
async def test_rigs_list_must_do_proper_http_request(sut, args, expected_url, api_key, aiohttp_request_mock):
    result = await sut.rigs_list(**args)

    assert RESPONSE_RV['result'] == result
    aiohttp_request_mock.assert_called_with(method='GET', url=expected_url,
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
async def test_rigs_info_must_do_proper_http_request(sut, api_key, aiohttp_request_mock):
    result = await sut.rig_info(rig_id=RIG_ID)

    assert RESPONSE_RV['result'] == result
    aiohttp_request_mock.assert_called_with(method='GET', url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rigs/{RIG_ID}/state',
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_args', [(dict(rig_id=RIG_ID, enable=True, power_cost=0.25), 
                                                 dict(isEnable=True, powerCost=0.25))])
async def test_set_rig_must_do_proper_http_request(sut, args, expected_args, api_key, 
                                                         aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.set_rig(**args)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='PUT', 
                                            url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rigs/{RIG_ID}', 
                                            json=expected_args,
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_args', [(dict(rig_id=RIG_ID, tariff_name='demo'), 
                                                 dict(rigHash=RIG_ID, tariffName='demo'))])
async def test_start_rent_must_do_proper_http_request(sut, args, expected_args, api_key, 
                                                         aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.start_rent(**args)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='POST', 
                                            url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rents/start', 
                                            json=expected_args,
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_args', [(dict(rent_id=RENT_ID), 
                                                 dict(hash=RENT_ID))])
async def test_stop_rent_must_do_proper_http_request(sut, args, expected_args, api_key, 
                                                         aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.stop_rent(**args)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='POST', 
                                            url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rents/stop', 
                                            json=expected_args,
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
async def test_rent_state_must_do_proper_http_request(sut, api_key, aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.rent_state(rent_id=RENT_ID)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='GET', url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rents/{RENT_ID}',
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
async def test_rent_info_must_do_proper_http_request(sut, api_key, aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.rent_state(rent_id=RENT_ID)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='GET', url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rents/{RENT_ID}',
                                            headers={'api-key': api_key}, raise_for_status=True)


@pytest.mark.asyncio
@pytest.mark.parametrize('args, expected_args', [(dict(rent_id=RENT_ID, enable=True, login='login', password='password'), 
                                                 dict(isEnable=True, login='login', password='password'))])
async def test_set_rent_must_do_proper_http_request(sut, args, expected_args, api_key, 
                                                         aiohttp_request_mock, resp_mock):
    resp_mock.json.return_value = dict(result='OK')
    result = await sut.set_rent(**args)

    assert 'OK' == result
    aiohttp_request_mock.assert_called_with(method='PUT', 
                                            url=f'{DEFAULT_BASE_URL}/api/{API_VERSION}/rents/{RENT_ID}', 
                                            json=expected_args,
                                            headers={'api-key': api_key}, raise_for_status=True)