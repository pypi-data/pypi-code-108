import asyncio

from unittest import IsolatedAsyncioTestCase

from eyja.main import Eyja

from eyja_nats import NATSHub


class SubscribeTest(IsolatedAsyncioTestCase):
    config = '''
        nats:
            host: localhost
            port: 18609
    '''

    received_data: dict

    async def asyncSetUp(self) -> None:
        await Eyja.init(
            config=self.config,
        )

        await NATSHub.init()
        return await super().asyncSetUp()

    async def test_subscribe(self):
        data = {'test':'123'}        

        async def handler(request: dict) -> dict:
            self.received_data = request

        await NATSHub.add_subscribe('test.sub', handler)
        await NATSHub.send('test.sub', {'test':'123'})

        await asyncio.sleep(2)

        self.assertEqual(data, self.received_data)

    async def test_request(self):
        data = {
            'a': 5,
            'b': 6,
        }

        async def handler(request: dict) -> dict:
            return {
                'sum': request.get('a', 1) + request.get('b', 1)
            }

        await NATSHub.add_subscribe('test.summation', handler)
        result = await NATSHub.request('test.summation', data)

        self.assertEqual(result.get('sum', 2), 11)
