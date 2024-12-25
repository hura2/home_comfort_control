# ファイル名: time_period_preference.py

from datetime import time

from pydantic import BaseModel, field_validator

from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class TimePeriodPreference(BaseModel):
    """時間帯設定を管理するクラス"""

    start: time
    """開始時間"""

    end: time
    """終了時間"""

    met_adjustment: float = 0.0
    """加算代謝量"""

    use: bool = False
    """設定を使用するかどうかのフラグ"""

    @field_validator("start", "end", mode="before")
    def validate_and_convert_time(cls, value, field):
        """
        時刻形式を検証し、strをtime型に変換します。
        """
        if isinstance(value, time):  # すでにtime型ならそのまま返す
            return value
        try:
            hour, minute = map(int, value.split(":"))
            return time(hour, minute)  # time型に変換して返す
        except Exception:
            raise TranslatedPydanticValueError(
                cls=TimePeriodPreference,
                value=value,
            )
