from asyncio import gather
from datetime import datetime
from unittest import IsolatedAsyncioTestCase, main


class TestClient(IsolatedAsyncioTestCase):
    async def test_import(self): # TODO do innego plinku
        import pymondis  # A ja sobie włączyłem usuwanie niepotrzebnych importów przed commitem, dlatego tu "pass" było
        _ = pymondis.__all__

    async def test_gets(self):
        from pymondis import Client
        async with Client() as client:
            await gather(
                client.get_crew(),
                client.get_camps(),
                client.get_plebiscite(datetime.now().year)
            )

    async def test_galleries(self):
        from pymondis import Client
        async with Client() as client:
            for castle in await client.get_castles():
                if not castle.active:
                    continue
                for gallery in await castle.get():
                    if gallery.empty:
                        continue
                    await (await gallery.get_photos())[0].normal.get()
                    break
                else:
                    continue
                break
            else:
                raise ValueError("Brak aktywnych zamków do przetestowania")


if __name__ == "__main__":
    main()
