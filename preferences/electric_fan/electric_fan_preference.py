from pydantic import BaseModel, Field

from preferences.electric_fan.auto_off_countermeasure_preference import AutoOffCountermeasurePreference


class ElectricFanPreference(BaseModel):
    """
    扇風機設定を管理するクラス。

    このクラスは扇風機に関連する設定値を保持し、
    各種温度設定をプロパティとして提供します。
    """

    fan_on_feels_like_temperature_threshold: float = Field(
        ..., ge=20, le=40, description="体感温度の閾値（20から40の範囲）"
    )
    """体感温度の閾値"""

    auto_off_countermeasure: AutoOffCountermeasurePreference = Field(
        ..., description="扇風機の8時間自動オフ対策"
    )
    """扇風機の8時間自動オフ対策"""
