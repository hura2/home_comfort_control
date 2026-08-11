from pydantic import BaseModel, Field


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
