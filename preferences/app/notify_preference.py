from pydantic import BaseModel, field_validator

from shared.enums.notification_channel import NotificationChannel
from shared.enums.notification_level import NotificationLevel
from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class NotifyPreference(BaseModel):
    """
    通知設定全体を管理するクラス
    """

    notifiers: list["NotifierPreference"]  # 通知設定のリスト
    """通知設定のリスト"""

    class NotifierPreference(BaseModel):
        """各通知設定を管理するクラス"""

        type: NotificationChannel  # 通知チャンネル（LINE, DISCORD など）
        """通知チャンネル"""
        category: NotificationLevel  # 通知レベル（IMPORTANT, NORMAL など）
        """通知レベル"""
        enabled: bool  # 通知有効フラグ
        """通知有効フラグ"""

        @field_validator("type", mode="before")
        def convert_type_to_enum(cls, value, field):
            # 文字列からEnumに変換
            try:
                value = NotificationChannel[value]
            except KeyError:
                raise TranslatedPydanticValueError(
                    cls=NotifyPreference,
                    type=value,
                )
            return value

        @field_validator("category", mode="before")
        def convert_category_to_enum(cls, value, field):
            # 文字列からEnumに変換
            try:
                value = NotificationLevel[value]
            except KeyError:
                raise TranslatedPydanticValueError(
                    cls=NotifyPreference,
                    category=value,
                )
            return value
