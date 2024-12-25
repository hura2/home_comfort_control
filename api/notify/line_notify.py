import requests

from api.notify.notify_interface import NotifyInterface
from util.env_config_loader import EnvConfigLoader

class LineNotify(NotifyInterface):
    """
    LINE Notifyを使ってメッセージを送信するクラス。

    Attributes:
        access_token (str): LINE Notify APIのアクセストークン
        url (str): LINE Notify APIのURL
        headers (dict): リクエストに必要なヘッダ情報
    """

    def __init__(self):
        """
        コンストラクタでLINE Notifyのアクセストークンを設定します。
        アクセストークンは環境変数から取得します。
        """
        self.url = "https://notify-api.line.me/api/notify"
        self.access_token = EnvConfigLoader.get_variable("LINE_NOTIFY_ACCESS_TOKEN")
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    def send_message(self, message: str) -> bool:
        """
        LINE Notifyを使ってメッセージを送信します。

        Args:
            message (str): 送信するメッセージ
        """
        payload = {'message': message}

        response = requests.post(self.url, headers=self.headers, params=payload)

        if response.status_code == 200:
            return True
        else:
            return False
