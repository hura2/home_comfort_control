from pydantic import BaseModel


class EffectiveOutdoorTemperature(BaseModel):
    """
    外気温度の有効値を表すクラス
    """

    outdoor_temperature: float | None
    """外気温度"""
    forecast_temperature: float | None
    """予測外気温度"""

    @property
    def value(self) -> float:
        """外気温度の有効値を取得する"""
        if self.outdoor_temperature is not None:
            return self.outdoor_temperature
        if self.forecast_temperature is not None:
            return self.forecast_temperature
        return 20
