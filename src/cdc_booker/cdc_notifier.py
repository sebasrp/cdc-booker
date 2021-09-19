import requests


class CDCNotifier:
    API_BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message):
        send_text = (
            CDCNotifier.API_BASE_URL
            + self.token
            + "/sendMessage?chat_id="
            + self.chat_id
            + "&parse_mode=Markdown&text="
            + message
        )

        response = requests.get(send_text)
        return response.json()

    def send_photo(self, image_path):
        data = {"chat_id": self.chat_id}
        url = f"{CDCNotifier.API_BASE_URL}{self.token}/sendPhoto"
        with open(image_path, "rb") as image_file:
            response = requests.post(url, data=data, files={"photo": image_file})
        return response.json()
