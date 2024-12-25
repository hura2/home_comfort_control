import json

import requests

from api.notify.notify_interface import NotifyInterface
from util.env_config_loader import EnvConfigLoader


class DiscordNotify(NotifyInterface):
    """
    DiscordのWebhookを使ってメッセージを送信するクラス。

    Attributes:
        webhook_url (str): Discord Webhook URL
    """

    def __init__(self):
        """
        コンストラクタでWebhook URLを環境変数から設定します。
        """
        self.webhook_url: str = EnvConfigLoader.get_variable("DISCORD_WEBHOOK_URL")

    def send_message(self, message: str) -> bool:
        """
        Discord Webhookにメッセージを送信します。

        Args:
            message (str): 送信するメッセージ
        """
        # Webhookに送るデータ
        data = {"content": message}  # メッセージ内容

        # POSTリクエストをWebhook URLに送信
        response = requests.post(
            self.webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )

        # 結果を確認
        if response.status_code == 204:
            return True
        else:
            return False
