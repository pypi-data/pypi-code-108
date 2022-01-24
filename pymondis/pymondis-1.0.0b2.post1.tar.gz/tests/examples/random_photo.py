"""
Pokazuje losowe zdjęcie z losowej galerii z losowego zamku (Może trochę zająć - 3 synchroniczne zapytania).
"""

from asyncio import run
from io import BytesIO
from random import choice

from PIL import Image  # pip install pillow

from pymondis import Client


async def main():
    async with Client() as client:
        for castle_galleries in await client.get_castles():
            if not castle_galleries.active:
                continue
            for gallery in await castle_galleries.get():
                if gallery.empty:
                    continue
                photos = await gallery.get_photos()
                if not photos:
                    continue
                photo_bytes = await choice(photos).large.get()
                break
            else:
                continue
            break
        else:
            print("Nie znaleziono żadnych zdjęć.")
        Image.open(BytesIO(photo_bytes)).show()

if __name__ == "__main__":
    run(main())
