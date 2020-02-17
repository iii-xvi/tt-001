_INCORRECT_INPUT = "Incorrect input, see example "
INTRODUCTION_MESSAGE = """Hello, i'm small change bot TT-01.
What i can:
/list - available rates
/exchange 10 USD to CAD - converts to the second currency with two decimal precision
/history USD/CAD for 7 days - image graph chart which shows the exchange rate graph/chart 
"""

LIST_HEADER = "Available rates:"
LIST_ROW = "{0}: {1:.2f}"
LIST_FOOTER = "\nBase: _{base}_\nDate: _{date}_"

EXCHANGE_MESSAGE_SYMBOL = "{0}{1:.2f}"
EXCHANGE_MESSAGE_CODE = "{0:.2f} {1}"
EXCHANGE_HELP = _INCORRECT_INPUT + "`/exchange 10 USD to CAD`"

HISTORY_MESSAGE = "History"
HISTORY_MISSING = "History missing for selected date"
HISTORY_HELP = _INCORRECT_INPUT + "`/history USD/CAD for 7 days`"

ERROR_MESSAGE = "API Error: {0.args}"
