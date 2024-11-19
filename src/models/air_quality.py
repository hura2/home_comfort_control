from typing import Optional

from util.humidity_metrics import HumidityMetrics


class AirQuality:
    """
    空気の質を表すクラス。
    """

    def __init__(self, temperature: float, humidity: float, co2_level: Optional[int] = None):
        self._temperature = temperature
        self._humidity = humidity
        self._co2_level = co2_level

    @property
    def temperature(self) -> float:
        """温度"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if value < -100 or value > 60:
            raise ValueError("温度は-100度から60度の間でなければなりません")
        self._temperature = value

    @property
    def humidity(self) -> float:
        """湿度"""
        return self._humidity

    @humidity.setter
    def humidity(self, value: float) -> None:
        if value < 0 or value > 100:
            raise ValueError("湿度は0から100の間でなければなりません")
        self._humidity = value

    @property
    def co2_level(self) -> Optional[int]:
        """CO2濃度"""
        return self._co2_level

    @co2_level.setter
    def co2_level(self, value: Optional[int]) -> None:
        """CO2濃度を設定する際のバリデーション"""
        if value is not None and value < 0:
            raise ValueError("CO2濃度は0以上でなければなりません")
        self._co2_level = value

    @property
    def absolute_humidity(self) -> float:
        """
        絶対湿度を計算するプロパティ。

        Returns:
            float: 絶対湿度 (g/m³)。
        """
        return HumidityMetrics.calculate_absolute_humidity(self.temperature, self.humidity)
