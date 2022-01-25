from __future__ import absolute_import

from mindsync.exc import MindsyncApiError

import aiohttp
import logging
import asyncio
import inspect
from urllib.parse import urljoin


def purge(obj):
    if isinstance(obj, dict):
        return dict((k, purge(v)) for k, v in obj.items() 
                    if (not isinstance(v, dict) and v is not None) or (isinstance(v, dict) and v))
    else:
        return obj


DEFAULT_BASE_URL = 'https://mainnet-api.mindsync.ai'
API_VERSION = '1.0'


class AsyncApi:
    def __init__(self, key, base_url=DEFAULT_BASE_URL):
        self.__logger = logging.getLogger(__name__)
        self.__key = key
        self.__base_url = base_url

# PROFILE

    async def profile(self, user_id=None):
        '''Gets profile.

        @param user_id User identifier to get profile for.
        @return Returns profile specified by user_id or own profile if user_id is None by default.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/users/client/profile' 
                      if user_id is None else f'/api/{API_VERSION}/users/profile/{user_id}')
        return await self.__get(url, 'Unable to get profile')


    async def set_profile(self, *, first_name=None, last_name=None, phone=None, gravatar=None, 
                          nickname=None, wallet_symbol=None, wallet_address=None, country=None, city=None):
        '''Sets profile info.'''

        args = dict(lastName=last_name, 
                    firstName=first_name, 
                    phone=phone, 
                    gravatar=gravatar, 
                    nickname=nickname, 
                    wallet=dict(symbol=wallet_symbol, address=wallet_address), 
                    country=country,
                    city=city)

        args = purge(purge(args))
        if not args:
            raise MindsyncApiError('Invalid arguments, nothing to set')

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/users/client/profile')
        return await self.__put(url, args, 'Unable to set profile')

# RIGS

# fixme: actually use params
    async def rigs_list(self, my=False, sort_by='rating', sort_dir='DESC', offset=1, limit=50):
        '''Gets rigs list.

        @param my Filter list to my rigs
        @param sort_by Designate the field to sort resulted list. Allows 'rating', 'cpu', 'gpuList',
                       'is_available'
        @return Returns rigs list in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rigs/my' if my else f'/api/{API_VERSION}/rigs')
        return await self.__get(url, 'Unable to get rigs list')


    async def rig_info(self, rig_id):
        '''Gets rig info.

        @param rig_id Rig's identifier within the platform.
        @return Returns rig information in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rigs/{rig_id}/state')
        return await self.__get(url, 'Unable to get rig info')


    async def set_rig(self, rig_id, enable, power_cost):
        '''Sets rig parameters.

        @param rig_id Rig's identifier within the platform.
        @param enable Whether rig is enabled, bool.
        @param power_cost The cost of the power, float number.
        @return Returns the result of operation metadata.
        '''
        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rigs/{rig_id}')
        args = purge(dict(isEnable=enable, powerCost=power_cost))
        if not args:
            raise MindsyncApiError('Invalid arguments, nothing to set')

        return await self.__put(url, args, 'Unable to set rig parameters')


    async def rig_tariffs(self, rig_id):
        '''Gets rig tariffs for all or certain rig.

        @param rig_id Rig's identifier within the platform.
        @return Returns tariffs information in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rigs/tariffs' if rig_id is None else f'/api/2.0/rigs/{rig_id}/tariffs')
        return await self.__get(url, 'Unable to get rig tarrifs')

# RENTS

    async def rents_list(self, my=False, sort_by='rating', sort_dir='DESC', offset=1, limit=50):
        '''Gets rents list.

        @param my Filter list to my rents
        @param sort_by Designate the field to sort resulted list. Allows 'rating', 'cpu', 'gpuList',
                       'is_available'
        @param sort_dir Sort direction.
        @return Returns active rents list in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/owner' if my else f'/api/{API_VERSION}/rents')
        return await self.__get(url, 'Unable to get rents list')


    async def start_rent(self, rig_id, tariff_name):
        '''Starts rent.

        @param rig_id Rig's identifier within the platform.
        @param tariff_name The tariff name to start the rent within.
        @return Returns the result of operation metadata.
        '''
        
        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/start')
        args = purge(dict(rigHash=rig_id, tariffName=tariff_name))
        if not args:
            raise MindsyncApiError('Invalid arguments')

        return await self.__post(url, args, 'Unable to start rent')


    async def stop_rent(self, rent_id):
        '''Stops rent.

        @param rent_id Rents's identifier in uuid format.
        @return Returns the result of operation metadata.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/stop')
        args = purge(dict(hash=rent_id))
        if not args:
            raise MindsyncApiError('Invalid arguments')

        return await self.__post(url, args, 'Unable to stop rent')


    async def rent_state(self, rent_id):
        '''Returns rent state.

        @param rent_id Rents's identifier in uuid format.
        @return Returns rent state in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/{rent_id}')
        return await self.__get(url, 'Unable to get rent state')


    async def rent_info(self, rent_id):
        '''Returns rent info.

        @param rent_id Rents's identifier.
        @return Returns rent info in JSON.
        '''

        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/{rent_id}')
        return await self.__get(url, 'Unable to get rent info')


    async def set_rent(self, rent_id, enable, login, password):
        '''Sets rent parameters.

        @param rent_id Rent's identifier within the platform.
        @param enable ...
        @param login Protect your rent with login/password
        @param password Protect your rent with login/password
        @return Returns the result of operation metadata.
        '''
        url = urljoin(self.__base_url, f'/api/{API_VERSION}/rents/{rent_id}')
        args = purge(dict(isEnable=enable, login=login, password=password))
        if not args:
            raise MindsyncApiError('Invalid arguments, nothing to set')

        return await self.__put(url, args, 'Unable to set rent parameters')


    async def __get(self, url, err_message):
        logger = self.__logger
        logger.debug(f'Get [{url}]')
        try:
            async with aiohttp.request(method='GET', url=url, 
                                    headers={'api-key': self.__key}, 
                                    raise_for_status=True) as resp:
                    result = await resp.json()
                    logger.debug(f'Result: {result}')
                    return result['result']
        except BaseException as e:
            self.__logger.debug(f'{err_message} [{repr(e)}]')
            raise MindsyncApiError(err_message) from e    



    async def __put(self, url, args, err_message):
        logger = self.__logger
        logger.debug(f'Put [url: {url}, args {args}]')
        try:
            async with aiohttp.request(method='PUT', url=url, json=args, 
                                       headers={'api-key': self.__key}, 
                                       raise_for_status=True) as resp:
                    result = await resp.json()
                    logger.debug(f'Result: {result}')
                    return result['result']
        except BaseException as e:
            self.__logger.debug(f'{err_message} [{repr(e)}]')
            raise MindsyncApiError(err_message) from e    


    async def __post(self, url, args, err_message):
        logger = self.__logger
        logger.debug(f'Post [url: {url}, args {args}]')
        try:
            async with aiohttp.request(method='POST', url=url, json=args, 
                                       headers={'api-key': self.__key}, 
                                       raise_for_status=True) as resp:
                    result = await resp.json()
                    logger.debug(f'Result: {result}')
                    return result['result']
        except BaseException as e:
            self.__logger.debug(f'{err_message} [{repr(e)}]')
            raise MindsyncApiError(err_message) from e    


class Api:
    def __init__(self, key, base_url=DEFAULT_BASE_URL):
        def wrap_method(func):
            def method(*args, **kwargs):
                return asyncio.run(func(*args, **kwargs))
            return method

        self.__async_api = AsyncApi(key, base_url)
        methods = inspect.getmembers(self.__async_api, predicate=inspect.ismethod)
        for m in methods:
            name, func = m
            if '__' not in name:
                setattr(self, name, wrap_method(func))
