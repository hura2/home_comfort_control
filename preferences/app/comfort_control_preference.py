from datetime import time
import re
from typing import List, Type

from pydantic import BaseModel, field_validator

from preferences.app.comfort_period_preference import ComfortPeriodPreference
from preferences.app.time_range_preference import TimeRangePreference
from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class ComfortControlPreference(BaseModel):
    enabled: bool
    """節電管理を有効にするかどうか"""

    solar_panel_enabled: bool
    """日光パネルを有効にするかどうか"""

    solar_active_hours: TimeRangePreference
    """日光パネルの有効時間のリスト"""

    solar_cloud_threshold: int
    """日光パネルの曇り度の閾値（％）"""

    environment_control_enabled: bool
    """湿度＋CO₂の快適管理を有効にするかどうか"""

    disabled_periods: List[ComfortPeriodPreference]
    """無効化する期間設定のリスト"""

    @field_validator("solar_active_hours", mode="before")
    def validate_solar_active_hours(cls, value: Type[TimeRangePreference] | None) -> TimeRangePreference:
        """
        solar_active_hours のバリデーションと変換を行う。

        - Noneの場合は、デフォルトの時間帯（0:00〜0:00）を返す。
        - 文字列の場合は "HH:MM-HH:MM" の形式を検証し、TimeRangePreference インスタンスを生成する。
        - dictの場合はTimeRangePreferenceのコンストラクタに展開してインスタンス化する。
        - すでにTimeRangePreferenceの場合はそのまま返す。
        - 上記以外は例外を投げる。
        """
        if value is None:
            # Noneの場合はデフォの時間帯を返す（必要に応じて変更可能）
            return TimeRangePreference(start_time=time(8, 0), end_time=time(16, 0))

        if isinstance(value, str):
            # 時刻範囲の正規表現チェック
            match = re.fullmatch(
                r"^([01]?\d|2[0-3]):([0-5]\d)-([01]?\d|2[0-3]):([0-5]\d)$",
                value
            )
            if not match:
                raise TranslatedPydanticValueError(cls=ComfortControlPreference, value=value)

            # 開始時刻と終了時刻をtime型に変換
            start = time(int(match.group(1)), int(match.group(2)))
            end = time(int(match.group(3)), int(match.group(4)))
            if end <= start:
                raise TranslatedPydanticValueError(cls=ComfortControlPreference, value=f"{start}-{end}")

            return TimeRangePreference(start_time=start, end_time=end)

        if isinstance(value, dict):
            # dictからTimeRangePreferenceインスタンス作成
            return TimeRangePreference(**value)

        if isinstance(value, TimeRangePreference):
            # 既にTimeRangePreferenceならそのまま返す
            return value

        # 上記に該当しなければエラー
        raise TranslatedPydanticValueError(cls=ComfortControlPreference, value=value)
