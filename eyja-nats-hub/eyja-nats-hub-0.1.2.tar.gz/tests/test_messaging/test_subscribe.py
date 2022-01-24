import asyncio

from unittest import IsolatedAsyncioTestCase
from pydantic import BaseModel
from eyja.main import Eyja

from eyja_nats import NATSHub


class CustomData(BaseModel):
    test: str
    is_close: bool

class CustomSumRequest(BaseModel):
    a: int
    b: int

class CustomSumResponse(BaseModel):
    sum: int

class SubscribeTest(IsolatedAsyncioTestCase):
    config = '''
        nats:
            host: localhost
            port: 18609
    '''

    received_data: dict
    received_custom_data: CustomData

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

    async def test_subscribe_with_custom_data(self):
        data = {
            'test':'456',
            'is_close': False,
        }        

        async def handler(request: CustomData):
            self.received_custom_data = request

        await NATSHub.add_subscribe('test.sub1', handler, data_cls=CustomData)
        await NATSHub.send('test.sub1', data)

        await asyncio.sleep(2)

        self.assertEqual(self.received_custom_data.test, '456')
        self.assertEqual(self.received_custom_data.is_close, False)

    async def test_request_with_custom_data(self):
        data = CustomSumRequest(
            a=7,
            b=8,
        )

        async def handler(request: CustomSumRequest) -> CustomSumResponse:
            return CustomSumResponse(
                sum=request.a+request.b,
            )

        await NATSHub.add_subscribe('test.summation1', handler, data_cls=CustomSumRequest)
        result: CustomSumResponse = await NATSHub.request('test.summation1', data, data_cls=CustomSumResponse)

        self.assertEqual(result.sum, 15)
