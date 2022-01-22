import aiohttp

from aiohttp.client_exceptions import ClientError
from typing import Optional, Union

from .exceptions import *

API_URL = 'https://api.anovaculinary.com/cookers/{cooker_id}{action}?secret={secret}'


class AnovaCookerLegacy:
    def __init__(self, cooker_id: str, cooker_secret: str):
        self.cooker_id = cooker_id
        self.cooker_secret = cooker_secret
        self.state = dict()

    async def _request(self, action: str = '', data: dict = None) -> dict:
        if '' != action:
            action = f'/{action}'

        url = API_URL.format(cooker_id=self.cooker_id, action=action, secret=self.cooker_secret)

        async with aiohttp.ClientSession(trust_env=True) as session:
            if data is not None:
                req = session.post(url, json=data)
            else:
                req = session.get(url)

            try:
                async with req as response:
                    if 401 == response.status:
                        raise AnovaCookerInvalidIdOrSecretException('Invalid Cooker id or secret')
                    elif 404 == response.status:
                        raise AnovaCookerOfflineException('Cooker offline')
                    elif 200 != response.status:
                        raise AnovaCookerUpdateFailedException(f'Cooker update failed with status: {response.status}')

                    return await response.json(content_type=None)
            except ClientError as e:
                raise AnovaCookerUpdateFailedException(f'API client error: {e}') from e

    async def update_state(self) -> dict:
        # {
        # 'cooker_id': 'anova f56-XXXXXXXXXXX',
        # 'firmware_version': 'ver 2.7.6',
        # 'is_running': True,
        # 'current_temp': 67.9,
        # 'target_temp': 131.5,
        # 'temp_unit': 'f',
        # 'speaker_mode': True,
        # 'current_job_id': '0abc5863-80e0-47ac-9baf-62a621d91700',
        # 'current_job': {
        #   'job_id': '0abc5863-80e0-47ac-9baf-62a621d91700',
        #   'job_type': 'manual_cook',
        #   'job_stage': 'preheating',
        #   'is_running': True,
        #   'target_temp': 131.5,
        #   'temp_unit': 'f',
        #   'timer_length': 960,
        #   'job_start_time': '2020-12-06T10:31:14.203631Z',
        #   'job_update_time': '0001-01-01T00:00:00Z',
        #   'preheat_estimate': 535000000000,
        #   'max_circulation_interval': 300,
        #   'threshold_temp': 40
        # },
        # 'is_timer_running': False,
        # 'timer_length': 960
        # }
        self.state = (await self._request())['status']
        return self.state

    @property
    def current_temperature(self) -> Optional[Union[int, float]]:
        return self.state.get('current_temp')

    @property
    def target_temperature(self) -> Optional[Union[int, float]]:
        return self.state.get('target_temp')

    @property
    def temperature_unit(self) -> Optional[str]:
        return self.state.get('temp_unit')

    @property
    def speaker_mode(self) -> Optional[bool]:
        return self.state.get('speaker_mode')

    @property
    def alarm_active(self) -> Optional[bool]:
        return self.state.get('alarm_active', False)

    @property
    def mode(self) -> Optional[str]:
        running = self.state.get('is_running')

        if running is None:
            return None
        elif running is False:
            return 'off'

        job = self.state.get('current_job') or {}
        return job.get('job_stage')

    @property
    def time_remaining(self) -> Optional[int]:
        return self.state.get('timer_length')

    async def set_target_temperature(self, temperature: Union[int, float]):
        await self._request(data={'target_temp': temperature})
        self.state['target_temp'] = temperature

    async def set_temperature_unit(self, unit: str):
        if unit not in ('', 'c', 'f'):
            raise ValueError(f'Invalid unit: {unit}')

        await self._request(data={'temp_unit': unit})
        self.state['temp_unit'] = unit

    async def set_speaker_mode(self, mode: bool):
        await self._request(data={'speaker_mode': mode})
        self.state['speaker_mode'] = mode

    async def stop_alarm(self):
        await self._request(data={'alarm_active': False})
        del self.state['alarm_active']

    async def create_job(self, temperature: Union[int, float], seconds: int):
        await self._request('jobs', data={
            'is_running': False,
            'job_id': '',
            'job_type': 'manual_cook',
            'max_circulation_interval': 300,
            'target_temp': temperature,
            'temp_unit': self.temperature_unit,
            'threshold_temp': 40,
            'timer_length': seconds
        })

    async def start_job(self):
        await self._request(data={'is_running': True})
        self.state['is_running'] = True

    async def stop_job(self):
        await self._request(data={'is_running': False})
        self.state['is_running'] = False
