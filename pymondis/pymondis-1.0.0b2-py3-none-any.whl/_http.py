from typing import Callable, NoReturn

from httpx import AsyncClient

from ._util import default_backoff
from .metadata import __title__ as project_name, __version__ as project_version


class HTTPClient(AsyncClient):
    """
    Podstawowa klasa bezpośrednio wykonująca zapytania.
    Zwraca surowe dane.
    Jest używana wewnętrznie przez klasę ``Client`` (zalecane jest korzystanie tylko z niego).
    """
    def __init__(
            self,
            timeout: float | None = None,
            backoff: Callable[[Callable], Callable] = default_backoff,
            *,
            base_url: str = "https://quatromondisapi.azurewebsites.net/api"
    ):
        """
        Initializuje instancję.

        :param timeout: czas, po którym client zostanie samoistnie rozłączony gdy, nie uzyska odpowiedzi.
        :param base_url: podstawowy url, na który będą kierowane zapytania (z wyjątkiem ``get_resource``).
        """
        super().__init__(timeout=timeout, base_url=base_url)
        self.headers = {"User-Agent": "{}/{}".format(project_name, project_version)}

        self.send = backoff(self.send)

    async def get_api_camps(self) -> list[dict[str, str | int | bool | None | list[str | dict[str, str | int]]]]:
        """
        Zwraca dane o aktualnych obozach.

        :returns: lista informacji o obozach.
        """
        response = await self.get(
            "/Camps",
            headers={"Accept": "application/json"}
        )
        return response.json()

    async def post_api_events_inauguration(self, reservation_model: dict):
        """
        Rezerwuje inaugurację.

        :param reservation_model: dane o rezerwacji.
        """
        await self.post(
            "/Events/Inauguration",
            json=reservation_model
        )

    async def get_api_images_galleries_castles(self) -> list[dict[str, str | int | bool]]:
        """
        Podaje czy dany zamek jest aktywny pod kątem galerii.

        :returns: lista ze statusami zamków.
        """
        response = await self.get(
            "/Images/Galeries/Castles",  # 'Galeries' - English 100
            headers={"Accept": "application/json"})

        return response.json()

    async def get_api_images_galleries_castle(self, castle: str) -> list[dict[str, str | int | bool]]:
        """
        Dostaje podstawowe dane na temat aktualnych galerii z danego zamku.

        :param castle: nazwa zamku, z którego pobierana jest lista galerii.
        :returns: lista reprezentująca aktualne galerie z zamku.
        """
        response = await self.get(
            "/Images/Galeries/Castle/{}".format(castle),  # Znowu 'Galeries'
            headers={"Accept": "application/json"})

        return response.json()

    async def get_api_images_galleries(self, gallery_id: int) -> list[dict[str, str]]:
        """
        Dostaje linki do zdjęć znajdujących się w galerii o danym ID.

        :param gallery_id: numer/ID galerii.
        :returns: lista linków do zdjęć w dwóch jakościach.
        """
        response = await self.get(
            "/Images/Galeries/{}".format(gallery_id),  # 'Galeries'...
            headers={"Accept": "application/json"})

        return response.json()

    async def post_api_orders_fourworldsbeginning(self, purchaser: dict):
        """
        Zamawia książkę „QUATROMONDIS – CZTERY ŚWIATY HUGONA YORCKA. OTWARCIE”.

        :param purchaser: dane o osobie zamawiającej.
        """
        await self.post(
            "/Orders/FourWorldsBeginning",
            json=purchaser
        )

    async def post_api_parentszone_survey(self, survey_hash: str, result: dict):
        """
        Prawdopodobnie nieobowiązujący już endpoint do jakiejś ankiety.

        :param survey_hash: ?
        :param result: opinia na temat obozu/obozów (?).
        """
        await self.post(
            "/ParentsZone/Survey/{}".format(survey_hash),
            json=result
        )

    async def get_api_parentszone_crew(self) -> list[dict[str, str]]:
        """
        Zwraca dane wszystkich psorów i kierowników.

        :returns: lista danych o kadrze
        """
        response = await self.get(
            "/ParentsZone/Crew",
            headers={"Accept": "application/json"}
        )

        return response.json()

    async def post_api_parentszone_apply(self):
        """
        Zgłasza cię do pracy.

        :raises ``NotImplementedError``: zawsze, bo metoda nie jest zaimplementowana -.-
        """
        raise NotImplementedError(
            "Ta metoda nie jest jeszcze zaimplementowana."
            "Zamiast niej możesz skorzystać z tradycyjnego formularza na stronie, śledząc wysyłane zapytania - "
            "może devtools w tab-ie NETWORK czy coś innego (nie znam się)."
            "Pamiętaj żeby nie wysyłać niczego gdy rzeczywiście nie chcesz zgłosić się do pracy."
            "Później otwórz nowy issue (https://github.com/Asapros/pymondis/issues (Implementacja zapytania POST)"
            "i podziel się nagranym zapytaniem (nie zapomnij za cenzurować danych osobowych)"
        )
        # Dane najprawdopodobniej są wysyłane jako form, ale nie ma tego w swagger-ze, a ja jestem borowikiem w
        # javascript-a i nie czaje, o co chodzi, dodajcie do dokumentacji pls

    async def post_api_reservations_subscribe(self, reservation_model: dict) -> list[str]:
        """
        Rezerwuje obóz.

        :param reservation_model: dane o osobie rezerwującej.
        :returns: lista kodów rezerwacji.
        """
        response = await self.post(
            "/Reservations/Subscribe",
            json=reservation_model,
            headers={"Accept": "application/json"}
        )

        return response.json()

    async def post_api_reservations_manage(self, pri: dict[str, str]) -> dict[str, str | bool]:
        """
        Dostaje dane o rezerwacji na podstawie jej kodu i nazwiska osoby rezerwującej.

        :param pri: kod i nazwisko.
        :returns: dokładniejsze dane o rezerwacji.
        """
        response = await self.post(
            "/Reservations/Manage",
            json=pri,
            headers={"Accept": "application/json"}
        )

        return response.json()

    async def patch_api_vote(self, category: str, name: str):
        """
        Głosuje na kandydata plebiscytu.

        :param category: kategoria, w której startuje kandydat.
        :param name: nazwa kandydata (najczęściej nazwisko).
        """
        await self.patch(  # A mnie dalej zastanawia, czemu tu patch jest, a nie post...
            "/Vote/{}/{}".format(category, name)
        )

    async def get_api_vote_plebiscite(self, year: int) -> list[dict[str, str | int | bool]]:
        """
        Zwraca surowe dane o kandydatach plebiscytu z danego roku (bez opisów :/).

        :param year: rok, z którego szukani są kandydaci (>= 2019).
        :returns: lista reprezentująca kandydatów.
        """
        response = await self.get(
            "/Vote/plebiscite/{}".format(year),  # Jedyny endpoint nie w PascalCase
            headers={"Accept": "application/json"}
        )

        return response.json()

    async def __aenter__(self) -> "HTTPClient":  # Type-hinting
        await super().__aenter__()
        return self

    def __enter__(self) -> NoReturn:
        raise RuntimeError("'with' nie można używać na HTTPClient'cie. Może chodziło ci o 'async with'?")

    def __exit__(self, exc_type, exc_val, exc_tb):
        return
