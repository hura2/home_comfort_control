from pydantic import BaseModel, Field

from preferences.circulator.temperature_thresholds_preference import \
    TemperatureThresholdsPreference


class ThresholdsPreference(BaseModel):
    """
    サーキュレーター設定を管理するクラス。

    このクラスはサーキュレーターに関連する設定値を保持し、
    各種温度設定をプロパティとして提供します。
    """
    
    high_temperature: list[TemperatureThresholdsPreference] = Field(
        ..., description="高温時の温度設定"
    )
    """高温時の温度設定"""

    normal_temperature: list[TemperatureThresholdsPreference] = Field(
        ..., description="高温以外の時の温度設定"
    )
    """高温以外の時の温度設定"""
