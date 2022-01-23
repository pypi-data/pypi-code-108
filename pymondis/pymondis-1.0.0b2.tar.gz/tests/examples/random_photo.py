"""
Pokazuje losowe zdjęcie z losowej galerii z losowego zamku (Może trochę zająć - 3 synchroniczne zapytania).
"""

from asyncio import run
from io import BytesIO
from random import choice

from PIL import Image  # pip install pillow
from httpx import HTTPStatusError

from pymondis import Castle, Client


async def main():
    async with Client() as client:
        tries = 0
        while tries < 10:
            tries += 1
            random_castle = choice(list(Castle))
            galleries = await client.get_galleries(random_castle)  # Pobiera galerie
            if not galleries:
                continue
            random_gallery = choice(galleries)
            photos = await random_gallery.get_photos()  # Pobiera zdjęcia
            if not photos:
                continue
            random_photo = choice(photos)
            try:
                image_data = await random_photo.large.get()  # Pobiera zawartość zdjęcia
            except HTTPStatusError as exception:
                if exception.response.status_code == 404:
                    print(
                        "Serwer podał ci link do zdjęcia, które z jakiegoś "
                        "powodu nie istnieje i zwala na ciebie, że się o nie pytasz. "
                        "To się często dzieje przy początku nowego sezonu."
                    )
                    continue
            Image.open(BytesIO(image_data)).show()  # Pokazuje zdjęcie
            return
    print("Podjęto {} prób i nie znaleziono żadnego zdjęcia (Może to początek sezonu?). Spróbuj ponownie później."
          .format(tries)
          )

if __name__ == "__main__":
    run(main())
