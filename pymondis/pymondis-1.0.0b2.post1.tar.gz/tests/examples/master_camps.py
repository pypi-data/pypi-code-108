"""
Pokazuje listę masterskich obozów od najmniejszej ceny.
"""


from asyncio import run

from pymondis import CampLevel, Client


async def main():
    async with Client() as client:
        camps = await client.get_camps()  # Pobiera listę obozów
        master_camps = filter(lambda camp: camp.level is CampLevel.MASTER, camps)  # Filtruje zostawiając masterskie
        master_camps_sorted = sorted(master_camps, key=lambda camp: camp.promo or camp.price)  # Sortuje wg. ceny
        for camp in master_camps_sorted:
            print(camp)

if __name__ == "__main__":
    run(main())