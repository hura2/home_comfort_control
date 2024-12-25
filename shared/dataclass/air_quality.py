from pydantic import BaseModel

from util.humidity_metrics import HumidityMetrics


class AirQuality(BaseModel):
    """
    空気の質を表すクラス。
    """

    temperature: float = -100
    """温度"""
    humidity: float = -100
    """湿度"""
    co2_level: int | None = None
    """CO2濃度"""

    @property
    def absolute_humidity(self) -> float:
        """
        絶対湿度を計算するプロパティ。

        Returns:
            float: 絶対湿度 (g/m³)。
        """
        return HumidityMetrics.calculate_absolute_humidity(self.temperature, self.humidity)
