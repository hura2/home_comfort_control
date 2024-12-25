from datetime import datetime

from pydantic import BaseModel


class WeatherHourly(BaseModel):
    """1時間ごとの気象データを表現するクラス"""

    datetime: datetime  # 日時
    """日時"""
    temperature: float  # 気温
    """気温"""
    humidity: float | None = None  # 湿度 (%)
    """湿度 (%)"""
    pressure: int | None = None  # 気圧 (hPa)
    """気圧 (hPa)"""
    wind_speed: float | None = None  # 風速 (m/s)
    """風速 (m/s)"""
    wind_direction: int | None = None  # 風向き (度)
    """風向き (度)"""
    precipitation_probability: float | None = None  # 降水確率
    """降水確率"""
    weather: str | None = None  # 天気
    """天気"""
    cloud_percentage: float | None = None  # 曇り度、%
    """曇り度、%"""
