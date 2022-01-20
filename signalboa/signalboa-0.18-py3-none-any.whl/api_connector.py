from dataclasses import dataclass
from datetime import datetime
from typing import List, AnyStr

import requests

from .enums import ALL_FREQUENCIES
from .exceptions import UnknownError, InvalidApiKey, UnavailablePair, UnsupportedFrequency


@dataclass
class Signal:
    time: datetime
    signal: AnyStr

    def __str__(self):
        return "{} at {}".format(self.signal, self.time)

    def __repr__(self):
        return "{} at {}".format(self.signal, self.time)


@dataclass
class Pair:
    coin: AnyStr
    frequency: AnyStr
    delayed: bool

    def __str__(self):
        if self.delayed:
            return "{} with frequency {} (delayed)".format(self.coin, self.frequency)
        return "{} with frequency {}".format(self.coin, self.frequency)

    def __repr__(self):
        if self.delayed:
            return "{} with frequency {} (delayed)".format(self.coin, self.frequency)
        return "{} with frequency {}".format(self.coin, self.frequency)


@dataclass
class PairSignals:
    pair: Pair
    signals: List[Signal]

    def __str__(self):
        return "\n{}\n{}".format(self.pair, self.signals)

    def __repr__(self):
        return "\n{}\n{}".format(self.pair, self.signals)


class SignalBoaConnector:
    _api_key: AnyStr
    SB_URL = "https://sb.brainalyzed.com"

    def __init__(self, api_key):
        self._api_key = api_key

    def get_available_pairs(self, include_delayed: bool = False) -> List[Pair]:
        """
        Returns a list of pairs available to user. User can see all pairs in the system with time delayed by 100
        durations and non-delayed ones depending on which subscription he has

        :param include_delayed: if true returns both delayed and non-delayed pairs that user can see non-delayed
        :return: List of Pair objects
        """
        r = requests.get(f"{self.SB_URL}/api/pairs?include_delayed={include_delayed}&token={self._api_key}")

        if r.status_code == 401:
            raise InvalidApiKey
        if r.status_code != 200:
            raise UnknownError('Server returned: ' + r.text)

        return [Pair(coin=c['coin'], frequency=c['frequency'], delayed=c['delayed']) for c in r.json()]

    def get_signals(self, coin: AnyStr, frequency: AnyStr) -> PairSignals:
        """
        Get signals from SignalBoa api

        :param coin: name of the coin that should be fetched
        :param frequency: frequency string for which signals should be fetched. Take a look at ALL_FREQUENCIES array
                          for supported values
        :return: PairSignals object
        """

        if frequency not in ALL_FREQUENCIES:
            raise UnsupportedFrequency(f"{frequency}. Take a look at ALL_FREQUENCIES array for supported values")

        r = requests.get(f"{self.SB_URL}/api/signals?frequency={frequency}&coin={coin}&token={self._api_key}")
        if r.status_code == 401:
            raise InvalidApiKey
        if r.status_code == 404:
            raise UnavailablePair(r.reason)

        data = r.json()
        return PairSignals(Pair(coin=data[0]['coin'],
                                frequency=data[0]['frequency'],
                                delayed=data[0]['delayed']),
                           signals=[Signal(time=s['time'], signal=s['signal']) for s in data[0]['signals']])

    def get_signals_bulk(self, coins: List[AnyStr], frequencies: List[AnyStr]) -> List[PairSignals]:
        """
        Get signals from SignalBoa api

        :param coins: names that should be fetched
        :param frequencies: list of frequency strings, each corresponding to a coin from coins list. Take a look at
                            ALL_FREQUENCIES array for supported values
        :return: List of PairSignals objects
        """

        if len(coins) != len(frequencies):
            raise AssertionError("Length of coins and frequencies must be the same.")

        for f in frequencies:
            if f not in ALL_FREQUENCIES:
                raise UnsupportedFrequency(f"{f}. Take a look at ALL_FREQUENCIES array for supported values")

        frequencies = map(lambda x: f"frequency={x}", frequencies)
        coins = map(lambda x: f"coin={x}", coins)

        r = requests.get(f"{self.SB_URL}/api/signals?{'&'.join(frequencies)}&{'&'.join(coins)}&token={self._api_key}")
        if r.status_code == 401:
            raise InvalidApiKey
        if r.status_code == 422:
            raise UnavailablePair(r.reason)

        ret = []
        for tmp in r.json():
            ret.append(PairSignals(Pair(coin=tmp['coin'],
                                        frequency=tmp['frequency'],
                                        delayed=tmp['delayed']),
                                   signals=tmp['signals']))

        return ret
