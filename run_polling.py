#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from exchange_bot import updater

if __name__ == '__main__':
    # start
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time,
    # since start_polling(...) is non-blocking and will stop the bot gracefully.
    updater.idle()
