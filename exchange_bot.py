import logging
import pickle
import re
import typing as T
from datetime import date

import bidict
import telegram
from dateparser.search import search_dates
from telegram.ext import Updater, Dispatcher, Filters, CommandHandler, MessageHandler

import config
from lib import locale, chart_maker, currencymap
from lib.exchange_api import ExchangeError
from lib.exchange_api.cache_wrapper import CacheWrapper
from lib.exchange_api.exchangeratesapi_io import ExchangeRatesAPIio

# enable logging
logging.basicConfig(format='[%(asctime)s|%(name)s|%(levelname)s]  %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

symbol_code_map = bidict.frozenbidict({
    curr_info['symbol']: curr_code
    for curr_code, curr_info in currencymap.get().items()
    if len(curr_info['symbol']) == 1  # only symbols
})

# init api
exchange_api = ExchangeRatesAPIio()

# == WARN ZONE ==
# i don't have enough time to write this in right way(

# get cache backend
if config.IS_LOCAL:
    import cachetools

    cache_backend = cachetools.TTLCache(64, ttl=config.CACHE_TTL_SECONDS)
else:
    import redis

    class RedisCacheBackend:
        def __init__(self, _redis):
            self._redis = _redis

        def get(self, key):
            value = self._redis.get(key)
            if not value:
                return
            return pickle.loads(value)

        def __setitem__(self, key, value):
            self._redis.set(key,
                            pickle.dumps(value),
                            ex=config.CACHE_TTL_SECONDS)

    cache_backend = RedisCacheBackend(redis.StrictRedis())

# == END WARN ZONE ==

# wrap api for caching
exchange_api = CacheWrapper(exchange_api, cache_backend)

# init telegram api
updater = Updater(config.TELEGRAM_TOKEN, use_context=True)
bot = updater.bot


def cmd_start(update, _context):
    """Send a message when the command `start` is issued."""
    update.message.reply_markdown(locale.INTRODUCTION_MESSAGE)


def cmd_list(update, _context):
    """List of all available rates from exchange API

    Example:
        -->  `/list` or `/lst`
        ```
        DKK: 6.74
        HUF: 299.56
        ```
    """
    result = exchange_api.get_rates()
    out_message = [locale.LIST_HEADER.format_map(result)]
    for currency, rate in result['rates'].items():
        out_message.append(locale.LIST_ROW.format(currency, rate))
    out_message.append(locale.LIST_FOOTER.format_map(result))
    update.message.reply_markdown("\n".join(out_message))


RE_SYMBOL_VALUE = re.compile("([^0-9]+)([0-9]+)")


def _parse_exchange_params(message: str) -> T.Optional[dict]:
    params = message.split()[1:]  # skip command

    # fail early
    if not params:
        return

    if len(params) == 2:
        groups = RE_SYMBOL_VALUE.match(params[0]).groups()
        return dict(value=float(groups[1]),
                    currencies=[symbol_code_map[groups[0]], params[1]])

    if len(params) == 3:
        return dict(value=float(params[0]), currencies=params[1:])

    if len(params) == 4 and params[2] == 'to':
        return dict(value=float(params[0]), currencies=[params[1], params[3]])


def cmd_exchange(update, _context):
    """Converts to the second currency with two decimal precision .

     Example:
        --> `/exchange $10 to CAD` or `/exchange 10 USD to CAD`
        `$15.55`
   """
    try:
        params = _parse_exchange_params(update.message.text)
    except ExchangeError as exc:
        update.message.reply_markdown(locale.ERROR_MESSAGE.format(exc=exc))
        return

    if not params:
        update.message.reply_markdown(locale.EXCHANGE_HELP)
        return

    result = exchange_api.get_rates(params['currencies'])

    value = params['value']

    # first convert to base currency
    if result['rates'][params['currencies'][0]] != 1:
        value /= result['rates'][params['currencies'][0]]

    # then to requested
    _currency_to = params['currencies'][1]
    if result['rates'][_currency_to] != 1:
        value *= result['rates'][_currency_to]

    symbol = symbol_code_map.inverse.get(_currency_to)
    if symbol:
        out_message = locale.EXCHANGE_MESSAGE_SYMBOL.format(symbol, value)
    else:
        out_message = locale.EXCHANGE_MESSAGE_CODE.format(value, _currency_to)

    update.message.reply_markdown(out_message)


def _parse_history_params(message: str) -> T.Optional[dict]:
    params = message.split(maxsplit=2)[1:]  # skip command

    # fail early
    if not params:
        return

    currencies = params[0].split("/")
    if len(currencies) != 2:
        return

    date_to = date.today()
    date_from = search_dates(params[1])
    if len(date_from) != 1:
        return
    date_from = date_from[0][1].date()

    return dict(
        currencies=currencies,
        date_from=date_from,
        date_to=date_to,
    )


def cmd_history(update, _context):
    """Show the exchange rate graph/chart of the selected currency
    for the last 7 days
    """
    params = _parse_history_params(update.message.text)
    if not params:
        update.message.reply_markdown(locale.HISTORY_HELP)
        return

    try:
        history = exchange_api.get_rates_history(**params)
    except ExchangeError as exc:
        update.message.reply_markdown(locale.ERROR_MESSAGE.format(exc))
        return

    if not history:
        update.message.reply_markdown(locale.HISTORY_MISSING)
        return

    _to_currency = params["currencies"][1]

    chart_image = chart_maker.make(
        ((dt, rate[_to_currency]) for dt, rate in history['rates'].items()),
        x_name="Date",
        y_name="/".join(params["currencies"]))

    update.message.reply_photo(
        chart_image,
        caption=locale.HISTORY_MESSAGE.format_map(params),
        parse_mode=telegram.ParseMode.MARKDOWN)


def on_error(update, context):
    """Log errors caused by Updates"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# set handlers
dp: Dispatcher = updater.dispatcher
dp.add_handler(CommandHandler("start", cmd_start))
dp.add_handler(CommandHandler("lst", cmd_list))
dp.add_handler(CommandHandler("list", cmd_list))
dp.add_handler(CommandHandler("exchange", cmd_exchange))
dp.add_handler(CommandHandler("history", cmd_history))
dp.add_handler(MessageHandler(Filters.text, cmd_start))

dp.add_error_handler(on_error)
