"""
Przydatne funkcje.
"""
from asyncio import run, sleep
from datetime import datetime
from functools import wraps

from httpx import AsyncClient, ConnectError, HTTPStatusError

from ._enums import EventReservationOption
from ._exceptions import HTTPClientLookupError


def default_backoff(function):
    """
    Dekorator funkcji wykonujących zapytania.

    :param function: funkcja do wrapowania.
    :returns: wrapowana funkcja.
    :raises HTTPStatusError: nie udało się pomyślnie wykonać zapytania (kod błędu 400-499 lub 3 próby zakończone >= 500).
    :raises ConnectError: problem z połączeniem.
    """

    @wraps(function)
    async def inner_backoff(*args, **kwargs):
        tries: int = 0
        while True:
            tries += 1
            try:
                response = await function(*args, **kwargs)
                response.raise_for_status()
                return response
            except HTTPStatusError as error:
                if tries >= 3:
                    raise
                if not error.response.is_server_error:
                    if error.response.is_client_error:
                        raise
                    return error.response
            except ConnectError:
                if tries >= 3:
                    raise

            await sleep(tries + 0.5)

    return inner_backoff


def synchronize(function):
    """
    Dekorator do zamiany funkcji asynchronicznych na synchroniczne.

    :param function: funkcja do wrapowania.
    :returns: wrapowana funkcja.
    """
    @wraps(function)
    def inner_synchronize(*args, **kwargs):
        return run(function(*args, **kwargs))
    return inner_synchronize


def choose_http(*http_clients: AsyncClient | None):
    for http_client in http_clients:
        if http_client is None or http_client.is_closed:
            continue
        return http_client
    raise HTTPClientLookupError()


def datetime_from_string(value: str) -> datetime:
    """
    Zamienia stringa na datetime (%Y-%m-%dT%H:%M:%S).

    :param value: string do zamiany.
    :returns: datetime ze stringa.
    """
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


def string_from_datetime(value: datetime) -> str:
    """
    Zamienia datetime na stringa (%Y-%m-%dT%H:%M:%S).

    :param value: datetime do zamiany.
    :returns: string z datetime.
    """
    return value.strftime("%Y-%m-%dT%H:%M:%S")


def datetime_converter(value: str | datetime) -> datetime:
    """
    Zamienia stringa na datetime (%Y-%m-%dT%H:%M:%S) jeśli to potrzebne.

    :param value: string do ewentualnej zamiany lub datetime.
    :returns: datetime ze stringa lub podany datetime.
    """
    return value if isinstance(value, datetime) else datetime_from_string(value)


def optional_character_converter(value: str) -> str | None:
    """
    Zamienia string-a "Nazwa postaci Quatromondis" na None.
    (ktoś stwierdził, że taki będzie placeholder dla imion magicznych psorów, którzy ich nie ustawili).

    :param value: string do ewentualnej zamiany.
    :returns: ``None`` jeśli string brzmiał "Nazwa postaci Quatromondis" lub podany string.
    """
    return None if value == "Nazwa postaci Quatromondis" else value


def optional_string_converter(value: str) -> str | None:
    """
    Zamienia pustego stringa na ``None``.
    (ktoś stwierdził, że taki będzie placeholder dla braku wycieczek na turnusie).

    :param value: string do ewentualnej zamiany.
    :returns: ``None`` jeśli string był pusty (długość 0) lub podany string.
    """
    return value if value else None


def price_from_ero(option: EventReservationOption) -> int:
    """
    Zamienia EventReservationOption na odpowiadającą cenę.

    :param option: opcja rezerwacji.
    :returns: cena rezerwacji.
    :raises ValueError: ta opcja nie ma przypisanej ceny.
    """
    match option:
        case EventReservationOption.CHILD:
            return 450
        case EventReservationOption.CHILD_AND_ONE_PARENT:
            return 900
        case EventReservationOption.CHILD_AND_TWO_PARENTS:
            return 1300

    raise ValueError("Opcja rezerwacji wydarzenia nie ma przypisanej ceny.")
