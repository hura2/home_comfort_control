from typing import List
from api.notify.discord_notify import DiscordNotify
from api.notify.line_notify import LineNotify
from api.notify.notify_manager import NotifyManager
from api.notify.notify_interface import NotifyInterface
from common import constants
from common.constants import NotificationCategory
from settings.general_settings import GeneralSettings

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
        for notifier, notification_category in notifiers:
            manager.add_notifier(notifier, notification_category)

        return manager

    @staticmethod
    def _create_notifiers() -> List[tuple[NotifyInterface, NotificationCategory]]:
        """
        通知先のリストを作成する。

        Returns:
            List[tuple[NotifyInterface, NotificationType]]: 通知インターフェースと通知タイプのペアのリスト。
        """
        settings = GeneralSettings()
        notifiers: List[tuple[NotifyInterface, NotificationCategory]] = []

        for notifier in settings.notify_settings.notifiers:
            if notifier.enable:
                if notifier.type == constants.NotifierType.LINE:
                    notifiers.append((LineNotify(), notifier.category))
                elif notifier.type == constants.NotifierType.DISCORD:
                    notifiers.append((DiscordNotify(), notifier.category))

        return notifiers
