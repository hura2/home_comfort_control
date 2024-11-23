from typing import List

from api.notify.discord_notify import DiscordNotify
from api.notify.line_notify import LineNotify
from api.notify.notify_manager import NotifyManager
from api.notify.notify_interface import NotifyInterface
from settings.general_settings import GeneralSettings


class NotifyFactory:
    """
    通知ハンドラー(NotificationManager)を生成するファクトリクラス。
    """

    @staticmethod
    def create_manager() -> NotifyManager:
        """
        NotificationManagerを作成し、通知先を登録する。

        Returns:
            NotificationManager: 登録済みの通知ハンドラー。
        """
        # 通知ハンドラーのインスタンスを作成
        manager = NotifyManager()

        # 通知先を追加
        notifiers = NotifyFactory._create_notifiers()
        for notifier in notifiers:
            manager.add_notifier(notifier)

        return manager

    @staticmethod
    def _create_notifiers() -> List[NotifyInterface]:
        """
        通知先のリストを作成する。

        Returns:
            List[NotifyInterface]: 通知インターフェースのリスト。
        """
        settings = GeneralSettings()
        notifiers: List[NotifyInterface] = []

        # 通知先を条件に応じて追加
        if settings.notify_settings.enable_line_notify:
            notifiers.append(LineNotify())
        if settings.notify_settings.enable_discord_notify:
            notifiers.append(DiscordNotify())

        return notifiers
