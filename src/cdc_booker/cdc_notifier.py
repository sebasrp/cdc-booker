import requests


class CDCNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message):
        send_text = (
            "https://api.telegram.org/bot"
            + self.token
            + "/sendMessage?chat_id="
            + self.chat_id
            + "&parse_mode=Markdown&text="
            + message
        )

        response = requests.get(send_text)
        return response.json()
