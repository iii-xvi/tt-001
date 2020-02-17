#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import config
from exchange_bot import updater, bot

if __name__ == '__main__':
    # start
    updater.start_webhook(
        listen='0.0.0.0',
        port=config.PORT,
        url_path=config.TELEGRAM_TOKEN,
    )
    bot.set_webhook(f"{config.WEBHOOK_URL}/{config.TELEGRAM_TOKEN}")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time,
    # since start_webhook(...) is non-blocking and will stop the bot gracefully.
    updater.idle()
