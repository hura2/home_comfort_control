from pydantic import BaseModel, Field


class TemperatureThresholdsPreference(BaseModel):
    """
    温度設定とファン速度設定を管理するクラス。

    高温時の温度設定やファン速度設定などを保持し、これらをプロパティとして提供します。
    """

    temperature_deff: float = Field(..., ge=0, le=5, description="高温時の温度設定")
    """高温時の温度設定（摂氏）"""

    speed: int = Field(..., ge=0, le=5, description="ファン速度設定（1-5）")
    """ファン速度設定（1-5）"""
