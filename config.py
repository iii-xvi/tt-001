import os

IS_LOCAL = "IS_LOCAL" in os.environ
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', 60 * 5))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get('PORT', '8443'))
