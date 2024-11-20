import os
import requests
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(".env")

class LineNotify:
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
        self.access_token = os.getenv("LINE_NOTIFY_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("LINE Notifyのアクセストークンが設定されていません。")
        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    def send_message(self, message: str):
        """
        LINE Notifyを使ってメッセージを送信します。

        Args:
            message (str): 送信するメッセージ
        """
        if not message.strip():
            raise ValueError("メッセージは空にできません。")

        payload = {'message': message}

        try:
            response = requests.post(self.url, headers=self.headers, params=payload)

            if response.status_code == 200:
                print("メッセージが正常に送信されました。")
            else:
                print(f"エラーが発生しました: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"通信エラーが発生しました: {e}")
