from api.notify.notify_interface import NotifyInterface


class NotifyManager:
    """
    複数の通知方法を管理・送信するクラス。
    """

    def __init__(self):
        self.notifiers = []

    def add_notifier(self, notifier: NotifyInterface):
        """通知先を追加する"""
        self.notifiers.append(notifier)

    def notify(self, message: str) -> list[bool]:
        """
        全ての通知先にメッセージを送信する。

        Args:
            message (str): 送信するメッセージ。

        Returns:
            list[bool]: 通知の送信結果（成功: True, 失敗: False）。
        """
        results = [notifier.send_message(message) for notifier in self.notifiers]
        return results
