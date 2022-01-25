import asyncio

from unittest import IsolatedAsyncioTestCase

from eyja.main import Eyja

from eyja_nats import (
    NATSHub,
    NATSRoute,
    NATSRouteGroup,
)


class RoutesTest(IsolatedAsyncioTestCase):
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

    async def test_single_route(self):
        data = {'test':'123'}        

        async def handler(request: dict) -> dict:
            self.received_data = request

        route = NATSRoute(
            queue='test.sub2',
            handler=handler
        )

        await NATSHub.add_route(route=route)
        await NATSHub.send('test.sub2', {'test':'123'})

        await asyncio.sleep(2)

        self.assertEqual(data, self.received_data)

    async def test_route_group(self):
        data = {
            'a': 7,
            'b': 5,
        }

        async def handler_sum(request: dict) -> dict:
            return {
                'sum': request['a'] + request['b']
            }

        async def handler_dif(request: dict) -> dict:
            return {
                'dif': request['a'] - request['b']
            }

        group = NATSRouteGroup(
            routes=[
                NATSRoute(queue='test.sum2', handler=handler_sum),
                NATSRoute(queue='test.dif2', handler=handler_dif),
            ]
        )

        await NATSHub.add_route_group(group)
        sum = await NATSHub.request('test.sum2', data)
        dif = await NATSHub.request('test.dif2', data)

        self.assertEqual(sum['sum'], 12)
        self.assertEqual(dif['dif'], 2)
