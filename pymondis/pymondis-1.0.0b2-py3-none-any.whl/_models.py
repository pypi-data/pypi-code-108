"""
Modele ułatwiające korzystanie z ``Client``a.
Wszystkie modele są tworzone za pomocą biblioteki ``attrs``.
Wszystkie modele są *frozen* - nie da się zmieniać w nich atrybutów (oprócz tych, które nie są (``Resource``)).
Wszystkie modele mają określone atrybuty (``__slots__``) co pozwala na szybszy dostęp i oszczędność do 30% pamięci.
"""

from datetime import datetime
from typing import AsyncIterator

from attr import Factory, attrib, attrs
from attr.converters import optional as optional_converter
from attr.validators import deep_iterable, instance_of as type_validator, optional as optional_validator

from ._enums import CampLevel, CrewRole, EventReservationOption, Season, SourcePoll, TShirtSize, World
from ._exceptions import InactiveCastleError, InvalidGalleryError, RevoteError
from ._http import HTTPClient
from ._util import (
    choose_http,
    datetime_converter,
    optional_character_converter,
    optional_string_converter,
    price_from_ero,
    string_from_datetime
)


@attrs(repr=True, slots=True, frozen=True, hash=True)
class ParentSurvey:
    """
    Jakaś opinia o obozach, już pewnie nie istnieje na stronach
        (na ``web.archive.org`` też nie ma).

    :ivar _http (param http): ``HTTPClient``, który będzie używany do wysłania ankiety.
    """
    _http = attrib(
        type=HTTPClient | None,
        default=None,
        validator=optional_validator(
            type_validator(HTTPClient)
        ),
        repr=False
    )

    def to_dict(self) -> dict:
        """
        Zamienia siebie na dicta.

        :returns: instancja klasy w formie dicta.
        :raises NotImplementedError: klasa nie jest zaimplementowana.
        """
        raise NotImplementedError(
            "Ta klasa jeszcze nie jest do końca zaimplementowana. "
            "Jeśli wiesz gdzie na stronie występuje form do wysłania na /api/ParentsZone/Survey/... "
            "możesz otworzyć nowy issue https://github.com/Asapros/pymondis/issues ('Implementacja zapytania POST') "
            "i się tym podzielić."
        )

    async def submit(self, survey_hash: str, http: HTTPClient | None = None):
        """
        Wrzuca ankietę.

        :param survey_hash: Dobre pytanie.
        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        """
        await choose_http(http, self._http).post_api_parentszone_survey(survey_hash, self.to_dict())


@attrs(repr=True, slots=True, frozen=True, hash=True)
class ReservationDetails:
    """
    Dokładniejsze dane o rezerwacji.
    """

    @classmethod
    def from_dict(cls, data: dict) -> "ReservationDetails":
        """
        Initializuje nową instancję za pomocą danych w dict'cie.

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :returns: instancja klasy.
        :raises NotImplementedError: klasa nie jest zaimplementowana.
        """
        raise NotImplementedError(
            "Ta klasa jeszcze nie jest do końca zaimplementowana. "
            "Jeśli masz zarezerwowany obóz i jego kod to możesz wysłać zapytanie przez "
            "HTTPClient.post_reservation_manage."
            "Otwórz nowy issue https://github.com/Asapros/pymondis/issues ('Implementacja zapytania POST') "
            "i podziel się wynikiem funkcji, nie zapomnij za cenzurować danych osobowych. "
            "Możesz też dołączyć do issue przypuszczenia do czego może być każde pole."
        )


@attrs(repr=True, slots=True)
class Resource:
    """
    Reprezentuje dane, najczęściej zdjęcie z serwera ``hymsresources.blob.core.windows.net``.

    :ivar url: link do danych.
    :ivar _http (param http): ``HTTPClient``, który będzie używany do pobrania resource'a.
    :ivar _cache_response (keyword cache_response): zapisana ostatnia odpowiedź serwera.
    """
    url = attrib(
        type=str,
        validator=type_validator(str)
    )
    _http = attrib(
        type=HTTPClient | None,
        default=None,
        validator=optional_validator(
            type_validator(HTTPClient)
        ),
        eq=False,
        repr=False
    )
    _cache_content = attrib(
        type=bytes | None,
        default=None,
        validator=optional_validator(
            type_validator(bytes)
        ),
        kw_only=True,
        eq=False,
        repr=False
    )
    _cache_etag = attrib(
        type=str | None,
        default=None,
        validator=optional_validator(
            type_validator(str)
        ),
        kw_only=True,
        eq=False,
        repr=False
    )
    _cache_last_modified = attrib(
        type=str | None,
        default=None,
        validator=optional_validator(
            type_validator(str)
        ),
        kw_only=True,
        eq=False,
        repr=False
    )

    async def get_stream(
            self,
            use_cache: bool = True,
            update_cache: bool = True,
            chunk_size: int | None = 1024,
            http: HTTPClient | None = None
    ) -> AsyncIterator[bytes]:
        """
        Otwiera strumień danych z linku.

        :param use_cache: użyć ostatniej zapisanej odpowiedzi, gdy dane się nie zmieniły?
        :param update_cache: zapisać odpowiedź do użycia później przez ``use_cache``?
        :param chunk_size: wielkość fragmentu iterowanych danych (w bajtach).
        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :returns: asynchroniczny iterator po fragmentach danych przesłanych przez serwer
        """
        # Lock-i działają wolniej w tym przypadku...
        headers = {}
        if use_cache:
            if self._cache_etag is not None:
                headers["If-None-Match"] = self._cache_etag
            if self._cache_last_modified is not None:
                headers["If-Modified-Since"] = self._cache_last_modified
        content: bytes = b""
        async with choose_http(http, self._http).stream(
            "GET",
            self.url,
            headers=headers
        ) as response:
            if response.status_code == 304:
                yield self._cache_content
                return
            async for chunk in response.aiter_bytes(chunk_size):
                content += chunk
                yield chunk
        if update_cache:
            self._cache_content = content
            self._cache_etag = response.headers["ETag"]
            self._cache_last_modified = response.headers["Last-Modified"]

    async def get(self, use_cache: bool = True, update_cache: bool = True, http: HTTPClient | None = None) -> bytes:
        """
        Całkowicie pobiera dane z linku.

        :param use_cache: użyć ostatniej zapisanej odpowiedzi, gdy dane się nie zmieniły?
        :param update_cache: zapisać odpowiedź do użycia później przez ``use_cache``?
        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :returns: dane po całkowitym ich pobraniu przez ``get_stream``.
        """
        content: bytes = b""
        async for chunk in self.get_stream(use_cache, update_cache, None, http):
            content += chunk
        return content


@attrs(repr=True, slots=True, frozen=True, hash=True)
class Gallery:
    """
    Reprezentuje galerię z fotorelacji.

    :cvar BLACKLIST: tuple ID usuniętych/uszkodzonych galerii.
    :ivar gallery_id: id galerii.
    :ivar start: data utworzenia galerii.
    :ivar end: data zakończenia galerii.
    :ivar name: nazwa galerii - ``Z jeśli zima + skrót zamku + numer``.
    :ivar empty: czy galeria jest pusta?
    :ivar _http (param http): ``HTTPClient``, który będzie używany do pobrania zdjęć z galerii
    """

    @attrs(repr=True, slots=True, frozen=True, hash=True)
    class Photo:
        """
        Reprezentuje zdjęcie z fotorelacji w dwóch rozdzielczościach.

        :ivar normal: zdjęcie słabej rozdzielczości.
        :ivar large: zdjęcie.
        """
        normal = attrib(
            type=Resource,
            validator=type_validator(Resource)
        )
        large = attrib(
            type=Resource,
            validator=type_validator(Resource)
        )

        @classmethod
        def from_dict(cls, data: dict, **kwargs) -> "Photo":
            r"""
            Initializuje nową instancję za pomocą danych w dict'cie.

            :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
            :param \**kwargs: dodatkowe argumenty, przekazywane dalej do konstruktorów ``Resource``.
            :returns: instancja klasy.
            """
            return cls(
                normal=Resource(data["AlbumUrl"], **kwargs),
                large=Resource(data["EnlargedUrl"], **kwargs)
            )

    BLACKLIST: tuple[int, ...] = (
        2, 6, 7, 8, 19, 20, 21, 22, 23, 24, 42, 53, 65, 69, 71, 76, 77, 85, 86, 92, 95, 107, 113, 135, 115, 129, 133
    )

    gallery_id = attrib(
        type=int,
        validator=type_validator(int)
    )
    start = attrib(
        type=datetime | None,
        converter=optional_converter(
            datetime_converter
        ),
        validator=optional_validator(
            type_validator(datetime)
        ),
        default=None
    )
    end = attrib(
        type=datetime | None,
        converter=optional_converter(
            datetime_converter
        ),
        validator=optional_validator(
            type_validator(datetime)
        ),
        default=None
    )
    name = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        ),
        default=None
    )
    empty = attrib(
        type=bool | None,
        validator=optional_validator(
            type_validator(bool)
        ),
        default=None
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=optional_validator(
            type_validator(HTTPClient),
        ),
        default=None,
        repr=False
    )

    async def get_photos(self, http: HTTPClient | None = None, *, ignore_blacklist: bool = False) -> list[Photo]:
        """
        Pobiera wszystkie zdjęcia z galerii.

        :param http: HTTPClient, który będzie użyty zamiast tego podanego w konstruktorze.
        :param ignore_blacklist: zignorować wystąpienie id galerii na blakliście?
        :returns: lista zdjęć.
        :raises InvalidGalleryError: galeria o tym ID najprawdopodobniej nie działa.
            (Ten wyjątek nie wzniesie się przy ``ignore_blacklist`` ustawionym na ``True``)
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        """
        if not ignore_blacklist and self.gallery_id in self.BLACKLIST:
            raise InvalidGalleryError(self.gallery_id)
        client = choose_http(http, self._http)
        photos = await client.get_api_images_galleries(self.gallery_id)
        return [
            self.Photo.from_dict(photo, http=client)
            for photo in photos
        ]

    @classmethod
    def from_dict(cls, data: dict[str, str | int | bool], **kwargs) -> "Gallery":
        r"""
        Initializuje nową instancję za pomocą danych w dict'cie.

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :param \**kwargs: dodatkowe argumenty, przekazywane dalej do konstruktora.
        :returns: instancja klasy.
        """
        return cls(
            gallery_id=data["Id"],
            start=data["StartDate"],
            end=data["EndDate"],
            name=data["Name"],
            empty=not data["HasPhotos"],
            **kwargs
        )


@attrs(repr=True, slots=True, frozen=True, hash=True)
class Castle:
    """
    Mówi o statusie zamku.

    :ivar name: nazwa zamku.
    :ivar castle_id: ID zamku.
    :ivar active: czy zamek posiada aktywne galerie?
    """
    name = attrib(
        type=str,
        validator=type_validator(str)
    )
    castle_id = attrib(
        type=int | None,
        validator=optional_validator(
            type_validator(int)
        ),
        default=None
    )
    active = attrib(
        type=bool | None,
        validator=optional_validator(
            type_validator(bool)
        ),
        default=None
    )
    _http = attrib(
        type=HTTPClient | None,
        default=None,
        validator=optional_validator(
            type_validator(HTTPClient)
        ),
        eq=False,
        repr=False
    )

    _ID_TO_NAME_MAP: dict[int, str] = {
        1:  "Zamek w Baranowie Sandomierskim",
        2:  "Zamek Czocha",
        3:  "Zamek Gniew",
        4:  "Zamek Golub Dobrzyń",
        5:  "Zamek Kliczków",
        6:  "Zamek w Krasiczynie",
        7:  "Zamek Moszna",
        8:  "Zamek w Nidzicy",
        9:  "Zamek w Pułtusku",
        10: "Pałac Racot",
        11: "Pałac Rybokarty",
        12: "Zamek Tuczno",
        13: "Pałac Witaszyce"
    }

    @classmethod
    def from_dict(cls, data: dict[str, int | bool], **kwargs) -> "Castle":
        r"""
        Initializuje nową instancję za pomocą danych w dict'cie.

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :param \**kwargs: dodatkowe argumenty, przekazywane dalej do konstruktora.
        :returns: instancja klasy.
        """
        return cls(
            cls._ID_TO_NAME_MAP[data["Id"]],
            data["Id"],
            data["IsActive"],
            **kwargs
        )

    async def get_galleries(self, http: HTTPClient | None = None, ignore_inactivity: bool = False) -> list[Gallery]:
        """
        Dostaje listę galerii z zamku.

        :param http: HTTPClient, który będzie użyty i podany do konstruktorów zamiast tego podanego w konstruktorze.
        :param ignore_inactivity: zignorować, że zamek jest nieaktywny?
        :returns: lista aktualnych galerii z zamku.
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        :raises InactiveCastleError: ten zamek jest nieaktywny.
            (Ten wyjątek nie wzniesie się przy ``ignore_inactivity`` ustawionym na ``True``)
        """
        if not ignore_inactivity and self.active is False:
            raise InactiveCastleError(self.name)
        client = choose_http(http, self._http)
        return [
            Gallery.from_dict(gallery, http=client)
            for gallery in await client.get_api_images_galleries_castle(self.name)
        ]


Castle.BARANOW = Castle("Zamek w Baranowie Sandomierskim", 1)
Castle.CZOCHA = Castle("Zamek Czocha", 2)
Castle.GNIEW = Castle("Zamek Gniew", 3)
Castle.GOLUB = Castle("Zamek Golub Dobrzyń", 4)
Castle.KLICZKOW = Castle("Zamek Kliczków", 5)
Castle.KRASICZYN = Castle("Zamek w Krasiczynie", 6)
Castle.MOSZNA = Castle("Zamek Moszna", 7)
Castle.NIDZICA = Castle("Zamek w Nidzicy", 8)
Castle.PLUTSK = Castle("Zamek w Pułtusku", 9)
Castle.RACOT = Castle("Pałac Racot", 10)
Castle.RYBOKARTY = Castle("Pałac Rybokarty", 11)
Castle.TUCZNO = Castle("Zamek Tuczno", 12)
Castle.WITASZYCE = Castle("Pałac Witaszyce", 13)


@attrs(repr=True, slots=True, frozen=True, hash=True)
class Camp:
    """
    Reprezentuje obóz.
    
    :ivar camp_id: id obozu.
    :ivar code: kod obozu ``Z, jeśli w zimę + skrót zamku + numer + skrót programu``
    :ivar place: zamek, w którym odbywa się obóz.
    :ivar price: cena obozu.
    :ivar promo: przeceniona cena, jeśli jest.
    :ivar active: aktywny? (nie ma listy rezerwowej).
    :ivar places_left: ilość pozostałych miejsc,
        ale jest zepsuta, bo czasem anomalnie rośnie i potrafi wynosić 75, kiedy jest lista rezerwowa...
    :ivar program: temat turnusu.
    :ivar level: poziom.
    :ivar world: świat.
    :ivar season: pora roku.
    :ivar trip: opisy wycieczki/wycieczek, jeśli jakieś są.
    :ivar start: data rozpoczęcia.
    :ivar end: data zakończenia.
    :ivar ages: lista zakresów wiekowych (ciekawe czego?).
    :ivar transports: transporty na miejsce.
    """

    @attrs(repr=True, slots=True, frozen=True, hash=True)
    class Transport:
        """
        Reprezentuje transport na obóz.

        :ivar city: nazwa miasta.
        :ivar one_way_price: cena w jedną stronę.
        :ivar two_way_price: cena w dwie strony.
        """
        city = attrib(
            type=str,
            validator=type_validator(str)
        )
        one_way_price = attrib(
            type=int,
            validator=type_validator(int)
        )
        two_way_price = attrib(
            type=int,
            validator=type_validator(int)
        )

        @classmethod
        def from_dict(cls, data: dict[str, str | int]) -> "Transport":
            """
            Initializuje nową instancję za pomocą danych w dict'cie.

            :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
            :returns: instancja klasy.
            """
            return cls(
                city=data["City"],
                one_way_price=data["OneWayPrice"],
                two_way_price=data["TwoWayPrice"]
            )

    camp_id = attrib(
        type=int,
        validator=type_validator(int)
    )
    code = attrib(
        type=str,
        validator=type_validator(str)
    )
    place = attrib(
        type=Castle,
        converter=Castle,
        validator=type_validator(Castle)
    )
    price = attrib(
        type=int,
        validator=type_validator(int)
    )
    promo = attrib(
        type=int | None,
        validator=optional_validator(
            type_validator(int)
        )
    )
    active = attrib(
        type=bool,
        validator=type_validator(bool)
    )
    places_left = attrib(
        type=int,
        validator=type_validator(int)
    )
    program = attrib(
        type=str,
        validator=type_validator(str)
    )
    level = attrib(
        type=CampLevel,
        converter=CampLevel,
        validator=type_validator(CampLevel)
    )
    world = attrib(
        type=World,
        converter=World,
        validator=type_validator(World)
    )
    season = attrib(
        type=Season,
        converter=Season,
        validator=type_validator(Season)
    )
    trip = attrib(
        type=str | None,
        converter=optional_string_converter,
        validator=optional_validator(
            type_validator(str)
        )
    )
    start = attrib(
        type=datetime,
        converter=datetime_converter,
        validator=type_validator(datetime)
    )
    end = attrib(
        type=datetime,
        converter=datetime_converter,
        validator=type_validator(datetime)
    )
    ages = attrib(
        type=list[str],
        validator=deep_iterable(
            type_validator(str)
        )
    )
    transports = attrib(
        type=list[Transport],
        validator=deep_iterable(
            type_validator(Transport)
        )
    )

    @classmethod
    def from_dict(cls, data: dict[str, str | int | bool | None | list[str | dict[str, str | int]]]) -> "Camp":
        """
        Initializuje nową instancję za pomocą danych w dict'cie

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :returns: instancja klasy.
        """
        return cls(
            data["Id"],
            data["Code"],
            data["Place"],
            data["Price"],
            data["Promo"],
            data["IsActive"],
            data["PlacesLeft"],
            data["Program"],
            data["Level"],
            data["World"],
            data["Season"],
            data["Trip"],
            data["StartDate"],
            data["EndDate"],
            data["Ages"],
            [
                cls.Transport.from_dict(transport)
                for transport in data["Transports"]
            ]
        )


@attrs(repr=True, slots=True, frozen=True, hash=True)
class Purchaser:
    """
    Reprezentuje osobę kupującą.

    :ivar name: imię.
    :ivar surname: nazwisko.
    :ivar email: email.
    :ivar phone: numer telefonu.
    :ivar parcel_locker: dane o paczkomacie.
    :ivar _http (param http): ``HTTPClient``, który będzie używany do wysłania zamówienia.
    """
    name = attrib(
        type=str,
        validator=type_validator(str)
    )
    surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    email = attrib(
        type=str,
        validator=type_validator(str)
    )
    phone = attrib(
        type=str,
        validator=type_validator(str)
    )
    parcel_locker = attrib(
        type=str,
        validator=type_validator(str)
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=optional_validator(
            type_validator(HTTPClient),
        ),
        default=None,
        repr=False
    )

    def to_dict(self) -> dict[str, str]:
        """
        Zamienia siebie na dicta.

        :returns: instancja klasy w formie dicta.
        """
        return {
            "Name":         self.name,
            "Surname":      self.surname,
            "Email":        self.email,
            "Phone":        self.phone,
            "ParcelLocker": self.parcel_locker
        }

    async def order_fwb(self, http: HTTPClient | None = None):
        """
        Zamawia książkę „QUATROMONDIS – CZTERY ŚWIATY HUGONA YORCKA. OTWARCIE”.

        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        """
        await choose_http(http, self._http).post_api_orders_four_worlds_beginning(self.to_dict())


@attrs(repr=True, slots=True, frozen=True, hash=True)
class PersonalReservationInfo:
    """
    Dane, za których pomocą możesz uzyskać szczegóły rezerwacji (kod i nazwisko).

    :ivar reservation_id: kod rezerwacji.
    :ivar surname: nazwisko zarezerwowanego.
    :ivar _http (param http): ``HTTPClient``, który będzie używany do dostania szczegółów rezerwacji
    """
    reservation_id = attrib(
        type=str,
        validator=type_validator(str)
    )
    surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=type_validator(HTTPClient),
        default=None,
        repr=False
    )

    def to_dict(self) -> dict[str, str]:
        """
        Zamienia siebie na dicta.

        :returns: instancja klasy w formie dicta.
        """
        return {
            "ReservationId": self.reservation_id,
            "Surname":       self.surname
        }

    async def get_details(self, http: HTTPClient | None = None) -> ReservationDetails:
        """
        Dostaje dane o rezerwacji,

        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :returns: szczegóły rezerwacji.
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        """
        return ReservationDetails.from_dict(
            await choose_http(http, self._http).post_api_reservations_manage(self.to_dict())
        )


@attrs(repr=True, slots=True, frozen=True, hash=True)
class Reservation:
    """
    Reprezentuje rezerwacje obozu.

    :ivar camp_id: id obozu.
    :ivar child: "główne" dziecko.
    :ivar parent_name: imię rodzica.
    :ivar parent_surname: nazwisko rodzica.
    :ivar nip: NIP rodzica.
    :ivar email: email.
    :ivar phone: numer telefonu.
    :ivar poll: źródło wiedzy o obozach.
    :ivar siblings: lista "pobocznych" dzieci.
    :ivar promo_code: kod promocyjny.
    :ivar _http (param http): ``HTTPClient``, który będzie używany do wysłania rezerwacji.
    """

    @attrs(repr=True, slots=True, frozen=True, hash=True)
    class Child:
        """
        Reprezentuje dziecko w rezerwacji.

        :ivar name: imię.
        :ivar surname: nazwisko.
        :ivar t_shirt_size: rozmiar koszulki.
        :ivar birthdate: data urodzenia.
        """
        name = attrib(
            type=str,
            validator=type_validator(str)
        )
        surname = attrib(
            type=str,
            validator=type_validator(str)
        )
        t_shirt_size = attrib(
            type=TShirtSize,
            validator=type_validator(TShirtSize)
        )
        birthdate = attrib(
            type=datetime,
            validator=type_validator(datetime)
        )

        def to_dict(self) -> dict[str, str]:
            """
            Zamienia siebie na dicta.

            :returns: instancja klasy w formie dicta.
            """
            return {
                "Name":    self.name,
                "Surname": self.surname,
                "Tshirt":  self.t_shirt_size.value,
                "Dob":     string_from_datetime(self.birthdate)
            }

    camp_id = attrib(
        type=int,
        validator=type_validator(int)
    )
    child = attrib(
        type=Child,
        validator=type_validator(Child)
    )
    parent_name = attrib(
        type=str,
        validator=type_validator(str)
    )
    parent_surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    nip = attrib(
        type=str,
        validator=type_validator(str)
    )
    email = attrib(
        type=str,
        validator=type_validator(str)
    )
    phone = attrib(
        type=str,
        validator=type_validator(str)
    )
    poll = attrib(
        type=SourcePoll,
        validator=type_validator(SourcePoll)
    )
    siblings = attrib(
        type=list[Child],
        validator=deep_iterable(
            type_validator(Child)
        ),
        factory=list
    )
    promo_code = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        ),
        default=None
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=optional_validator(
            type_validator(HTTPClient)
        ),
        default=None,
        repr=False
    )

    def to_dict(self) -> dict[str, int | dict[str, dict[str, str] | list[dict[str, str]]] | dict[str, str]]:
        """
        Zamienia siebie na dicta.

        :returns: instancja klasy w formie dicta.
        """
        return {
            "SubcampId": self.camp_id,
            "Childs":    {  # English 100
                "Main":     self.child.to_dict(),
                "Siblings": [sibling.to_dict() for sibling in self.siblings]
            },
            "Parent":    {
                "Name":    self.parent_name,
                "Surname": self.parent_surname,
                "Nip":     self.nip
            },
            "Details":   {
                "Email": self.email,
                "Phone": self.phone,
                "Promo": self.promo_code,
                "Poll":  self.poll.value
            }
        }

    def to_pri(self, **kwargs) -> PersonalReservationInfo:
        r"""
        Tworzy instancję ``PersonalReservationInfo`` na podstawie siebie.

        :param \**kwargs: argumenty podawane dalej do konstruktora.
        :returns: odpowiadające ``PersonalReservationInfo``.
        """
        return PersonalReservationInfo(self.camp_id, self.parent_surname, **{"http": self._http} | kwargs)

    async def reserve_camp(self, http: HTTPClient | None = None) -> list[str]:
        """
        Rezerwuje obóz na podstawie informacji w tym obiekcie.

        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :returns: lista kodów rezerwacji.
        """
        return await choose_http(http, self._http).post_api_reservations_subscribe(self.to_dict())


@attrs(repr=True, slots=True, frozen=True, hash=True)
class EventReservation:
    """
    Reprezentuje rezerwacje wydarzenia (tylko inauguracja)

    :ivar option: opcja rezerwacji.
    :ivar name: imię dziecka.
    :ivar surname: nazwisko dziecka.
    :ivar parent_name: imię rodzica.
    :ivar parent_surname: nazwisko rodzica.
    :ivar parent_reused: czy użyć ``parent_name`` i ``parent_surname`` zamiast
        ``first_parent_name`` i ``first_parent_surname``?
    :ivar phone: numer telefonu.
    :ivar email: email.
    :ivar first_parent_name: imię pierwszego rodzica do rezerwacji.
    :ivar first_parent_surname: nazwisko pierwszego rodzica do rezerwacji.
    :ivar second_parent_name: imię drugiego rodzica do rezerwacji.
    :ivar second_parent_surname: nazwisko drugiego rodzica do rezerwacji.
    ։ivar third_parent_name։ imię trzeciego rodzica do rezerwa... Dobra, żartuję.
    :ivar price: cena rezerwacji (jak ją zmienisz to *chyba* nie zarezerwujesz sobie taniej ;P).
    :ivar _http (param http): ``HTTPClient``, który będzie używany do wysłania rezerwacji.
    """
    option = attrib(
        type=EventReservationOption,
        converter=EventReservationOption,
        validator=type_validator(EventReservationOption)
    )
    name = attrib(
        type=str,
        validator=type_validator(str)
    )
    surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    parent_name = attrib(
        type=str,
        validator=type_validator(str)
    )
    parent_surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    parent_reused = attrib(
        type=bool,
        validator=type_validator(bool)
    )
    phone = attrib(
        type=str,
        validator=type_validator(str)
    )
    email = attrib(
        type=str,
        validator=type_validator(str)
    )
    first_parent_name = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        )
    )
    first_parent_surname = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        )
    )
    second_parent_name = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        )
    )
    second_parent_surname = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        )
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=type_validator(HTTPClient),
        default=None,
        repr=False
    )
    price = attrib(
        type=int,
        validator=type_validator(int),
        default=Factory(lambda self: price_from_ero(self.option), takes_self=True),
        kw_only=True
    )

    def to_dict(self) -> dict[str, str | int | bool]:
        """
        Zamienia siebie na dicta.

        :returns: instancja klasy w formie dicta.
        """
        data = {
            "Price":          self.price,
            "Name":           self.name,
            "Surname":        self.surname,
            "ParentName":     self.parent_name,
            "ParentSurname":  self.parent_surname,
            "IsParentReused": self.parent_reused,
            "Phone":          self.phone,
            "Email":          self.email
        }
        # TODO co się tutaj wydarzyło
        if self.option in (EventReservationOption.CHILD, EventReservationOption.CHILD_AND_PARENT):
            data.update(
                {"FirstParentName": self.first_parent_name, "FirstParentSurname": self.first_parent_surname}
            )
        if self.option is EventReservationOption.CHILD_AND_TWO_PARENTS:
            data.update(
                {"SecondParentName": self.second_parent_name, "SecondParentSurname": self.second_parent_surname}
            )
        return data

    async def reserve_inauguration(self, http: HTTPClient | None):
        """
        Rezerwuje inaugurację.

        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :raises HTTPClientLookupError: nie znaleziono otwartego ``HTTPClient``a.
        """
        await choose_http(http, self._http).post_api_events_inauguration(self.to_dict())


@attrs(repr=True, slots=True, frozen=True, hash=True)
class CrewMember:
    """
    Członek kadry (nie biuro ani HY).

    :ivar name: imię.
    :ivar surname: nazwisko.
    :ivar character: imię psorskie (czasem nie wpisane).
    :ivar position: rola.
    :ivar description: opis.
    :ivar photo: zdjęcie.
    """
    name = attrib(
        type=str,
        validator=type_validator(str)
    )
    surname = attrib(
        type=str,
        validator=type_validator(str)
    )
    character = attrib(
        type=str | None,
        converter=optional_character_converter,
        validator=optional_validator(
            type_validator(str)
        )
    )
    position = attrib(
        type=CrewRole,
        converter=CrewRole,
        validator=type_validator(CrewRole)
    )
    description = attrib(
        type=str,
        validator=type_validator(str)
    )
    photo = attrib(
        type=Resource,
        validator=type_validator(Resource)
    )

    @classmethod
    def from_dict(cls, data: dict[str, str], **kwargs) -> "CrewMember":
        r"""
        Initializuje nową instancję za pomocą danych w dict'cie.

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :param \**kwargs: argumenty podane do instancji zdjęcia.
        :returns: instancja klasy.
        """
        return cls(
            name=data["Name"],
            surname=data["Surname"],
            character=data["Character"].strip(),
            position=data["Position"],
            description=data["Description"],
            photo=Resource(data["PhotoUrl"], **kwargs)
        )


@attrs(repr=True, slots=True, frozen=True, hash=True)
class PlebisciteCandidate:
    """
    Kandydat plebiscytu.

    :ivar name: reprezentująca nazwa (najczęściej nazwisko).
    :ivar category: kategoria, w której startuje.
    :ivar votes: liczba głosów (``None`` jeśli są ukryte).
    :ivar plebiscite: nazwa plebiscytu.
    :ivar voted: czy już dzisiaj wydano głos na tę kategorię z tego IP.
    :ivar _http (param http): ``HTTPClient``, który będzie używany do oddania głosu.
    """
    name = attrib(
        type=str,
        validator=type_validator(str)
    )
    category = attrib(
        type=str,
        validator=type_validator(str)
    )
    votes = attrib(
        type=int | None,
        validator=optional_validator(
            type_validator(int)
        ),
        default=None
    )
    plebiscite = attrib(
        type=str | None,
        validator=optional_validator(
            type_validator(str)
        ),
        default=None
    )
    voted = attrib(
        type=bool | None,
        validator=optional_validator(
            type_validator(bool)
        ),
        default=None
    )
    _http = attrib(
        type=HTTPClient | None,
        validator=optional_validator(
            type_validator(HTTPClient)
        ),
        default=None,
        repr=False
    )

    @classmethod
    def from_dict(cls, data: dict[str, str | int | bool | None], **kwargs) -> "PlebisciteCandidate":
        """
        Initializuje nową instancję za pomocą danych w dict'cie.

        :param data: dict, na podstawie którego zostanie stworzona nowa instancja.
        :returns: instancja klasy.
        """
        return cls(
            name=data["Name"],
            votes=data["Result"],
            category=data["Category"],
            plebiscite=data["Plebiscite"],
            voted=data["WasVoted"],
            **kwargs
        )

    async def vote(self, http: HTTPClient | None = None, *, ignore_revote: bool = False):
        """
        Głosuje na kandydata.

        :param http: ``HTTPClient``, który będzie użyty zamiast tego podanego w konstruktorze.
        :param ignore_revote: zignorować, że głos już został oddany w tej kategorii?
        :raises RevoteError: podjęta została próba zagłosowania drugi raz na tą samą kategorię.
            (Ten wyjątek nie wzniesie się przy ``ignore_revote`` ustawionym na ``True``).
        """
        if not ignore_revote and self.voted:
            raise RevoteError(self.category)
        await choose_http(http, self._http).patch_api_vote(self.category, self.name)


Photo = Gallery.Photo
Transport = Camp.Transport
Child = Reservation.Child
