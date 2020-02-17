import typing as T
from datetime import date

import requests
from dateutil import parser as dateutil_parser

from . import ExchangeAPI, RatesResponse, RatesHistoryResponse, ExchangeError


class ExchangeRatesAPIio(ExchangeAPI):
    HOST = "https://api.exchangeratesapi.io/"

    def _post_init(self):
        self._sess = requests.session()

    def get_rates(self, currencies: T.List[str] = None) -> RatesResponse:
        currencies = currencies or []
        res = self._get("latest", symbols=",".join(currencies))
        res['date'] = dateutil_parser.parse(res['date']).date()
        return res

    def get_rates_history(self, currencies: T.List[str], date_from: date, date_to: date) \
            -> RatesHistoryResponse:
        res = self._get("history",
                        base=currencies[0],
                        symbols=",".join(currencies[1:]),
                        start_at=f"{date_from}",
                        end_at=f"{date_to}")
        for _date in list(res['rates'].keys()):
            res['rates'][dateutil_parser.parse(
                _date).date()] = res['rates'].pop(_date)

        res['date_from'] = dateutil_parser.parse(res.pop('start_at')).date()
        res['date_to'] = dateutil_parser.parse(res.pop('end_at')).date()
        return res

    def _get(self, url, **kwargs) -> T.Dict[str, T.Any]:
        kwargs.setdefault('base', self.base)
        data = self._sess.get(f"{self.HOST}{url}", params=kwargs).json()

        if "error" in data:
            raise ExchangeError(data['error'])

        return data
