import typing as T

import requests

JSON_URL = "https://www.localeplanet.com/api/auto/currencymap.json"


def get() -> T.Dict[str, str]:
    return requests.get(JSON_URL).json()
