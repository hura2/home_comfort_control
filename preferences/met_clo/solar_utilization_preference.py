from datetime import time

from pydantic import BaseModel, Field, field_validator

from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class SolarUtilizationPreference(BaseModel):
    """
    太陽光利用設定を管理するクラス
    """

    heating_reduction: "HeatingReductionPreference"
    """暖房抑制設定"""


class HeatingReductionPreference(BaseModel):
    """暖房抑制を管理するクラス"""

    enabled: bool
    """暖房抑制の有効化"""
    start_time: time
    """暖房抑制を開始する時間"""
    end_time: time
    """暖房抑制を終了する時間"""
    cloudiness_threshold: int = Field(..., ge=0, le=100)
    """太陽が出ているかの判断基準（曇り度、0～100）"""
    met_adjustment: float = Field(..., ge=0.0, le=1.0)
    """活動量に対する加算代謝量"""

    @field_validator("start_time", "end_time", mode="before")
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
                cls=HeatingReductionPreference,
                value=value,
            )
