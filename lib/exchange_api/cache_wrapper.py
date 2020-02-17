import typing as T
from datetime import datetime

from . import ExchangeAPI, RatesResponse


class CacheBackend(T.Protocol):
    """Simple cache backend interface"""

    def get(self, key: str) -> T.Optional[object]:
        pass

    def __setitem__(self, key: str, value: object):
        pass


class CacheWrapper(ExchangeAPI):
    def __init__(self, api: ExchangeAPI, backend: CacheBackend):
        super().__init__()
        self._api = api
        self._backend = backend

    def get_rates(self, currencies: T.List[str] = None) -> RatesResponse:
        _key = "ex:" + (";".join(currencies) if currencies else "all")
        value: T.Optional[RatesResponse] = self._backend.get(_key)
        if not value:
            value = self._api.get_rates(currencies)
            self._backend[_key] = value

        return value

    def get_rates_history(self, currencies: T.List[str], date_from: datetime,
                          date_to: datetime):
        """Don't cache history"""
        return self._api.get_rates_history(currencies, date_from, date_to)
