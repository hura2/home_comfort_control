from api.notify.discord_notify import DiscordNotify
from api.notify.line_notify import LineNotify
from api.notify.notify_interface import NotifyInterface
from api.notify.notify_manager import NotifyManager
from settings import app_preference
from shared.enums.notification_channel import NotificationChannel
from shared.enums.notification_level import NotificationLevel


class NotifyFactory:
    """
    通知マネージャ（NotifyManager）を生成するファクトリクラス。
    """

    @staticmethod
    def create_manager() -> NotifyManager:
        """
        NotifyManagerを作成し、通知先を登録する。

        Returns:
            NotifyManager: 登録済みの通知マネージャ。
        """
        manager = NotifyManager()
        notifiers = NotifyFactory._create_notifiers()

        # 通知先を登録
        for notifier, notification_level in notifiers:
            manager.add_notifier(notifier, notification_level)

        return manager

    @staticmethod
    def _create_notifiers() -> list[tuple[NotifyInterface, NotificationLevel]]:
        """
        通知先のリストを作成する。

        Returns:
            list[tuple[NotifyInterface, NotificationType]]: 通知インターフェースと通知タイプのペアのリスト。
        """
        notifiers: list[tuple[NotifyInterface, NotificationLevel]] = []

        for notifier in app_preference.notify.notifiers:
            if notifier.enabled:
                if notifier.type == NotificationChannel.LINE:
                    notifiers.append((LineNotify(), NotificationLevel.NORMAL))
                elif notifier.type == NotificationChannel.DISCORD:
                    notifiers.append((DiscordNotify(), NotificationLevel.NORMAL))

        return notifiers
