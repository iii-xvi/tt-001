import abc
import typing as T
from datetime import datetime

CurrencyRatePair = T.Dict[str, float]


class ExchangeError(Exception):
    """Base exchange error"""


class RatesResponse(T.TypedDict):
    rates: CurrencyRatePair
    base: str
    dt: datetime


class RatesHistoryResponse(T.TypedDict):
    rates: T.Dict[datetime, CurrencyRatePair]
    base: str
    dt_from: datetime
    dt_to: datetime


class ExchangeAPI(abc.ABC):
    def __init__(self, base="USD"):
        self.base = base
        self._post_init()

    def _post_init(self):
        pass

    @abc.abstractmethod
    def get_rates(self, currencies: T.List[str] = None) -> RatesResponse:
        pass

    @abc.abstractmethod
    def get_rates_history(self, currencies: T.List[str], date_from: datetime,
                          date_to: datetime) -> T.List[RatesResponse]:
        pass
