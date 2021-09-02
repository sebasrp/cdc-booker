import requests


class CDCNotifier:
    TOKEN = "your_telegram_token"
    CHAT_ID = "your_telegram_chat_id"

    @staticmethod
    def send_message(message):
        send_text = (
            "https://api.telegram.org/bot"
            + CDCNotifier.TOKEN
            + "/sendMessage?chat_id="
            + CDCNotifier.CHAT_ID
            + "&parse_mode=Markdown&text="
            + message
        )

        response = requests.get(send_text)
        return response.json()
