import os
import requests


def send_telegram_alert(message):
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token:
            return False, "Missing TELEGRAM_BOT_TOKEN"

        if not chat_id:
            return False, "Missing TELEGRAM_CHAT_ID"

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        response = requests.post(url, data=payload, timeout=10)

        if response.status_code == 200:
            return True, "Telegram alert sent."
        else:
            return False, response.text

    except Exception as e:
        return False, str(e)
