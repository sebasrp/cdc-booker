import requests


class CDCNotifier:
    TOKEN = "1974466016:AAHQGUykORF_bxcQ-Kl6sif0Do9Ya-L0aOs"
    CHAT_ID = "1360825641"

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
