from api.notify.notify_interface import NotifyInterface
from shared.enums.notification_level import NotificationLevel


class NotifyManager:
    """
    通知を種類ごとに管理し、送信するクラス。
    """

    def __init__(self):
        self.normal_notifiers: list[NotifyInterface] = []  # 通常通知先リスト
        self.important_notifiers: list[NotifyInterface] = []  # 重要通知先リスト

    def add_notifier(self, notifier: NotifyInterface, notification_category: NotificationLevel):
        """
        通知先を追加する。

        Args:
            notifier (NotifyInterface): 通知インターフェース。
            notification_type (NotificationType): 通知タイプ（通常 or 重要）。
        """
        if notification_category == NotificationLevel.NORMAL:
            self.normal_notifiers.append(notifier)
        elif notification_category == NotificationLevel.IMPORTANT:
            self.important_notifiers.append(notifier)

    def notify_normal(self, message: str | None) -> list[bool]:
        """
        通常通知を全ての通知先に送信する。

        Args:
            message (str): 送信するメッセージ。

        Returns:
            List[bool]: 通知結果（成功: True, 失敗: False）。
        """
        return [notifier.send_message(message or "") for notifier in self.normal_notifiers]

    def notify_important(self, message: str | None) -> list[bool]:
        """
        重要通知を全ての通知先に送信する。

        Args:
            message (str): 送信するメッセージ。

        Returns:
            List[bool]: 通知結果（成功: True, 失敗: False）。
        """
        return [notifier.send_message(message or "") for notifier in self.important_notifiers]
