from pydantic import BaseModel

from preferences.met_clo.high_temperature_preference import HighTemperaturePreference
from preferences.met_clo.low_temperature_preference import LowTemperaturePreference
from preferences.met_clo.solar_utilization_preference import SolarUtilizationPreference


class MetCloPreference(BaseModel):
    """
    温度に基づく衣服活動設定を管理するクラス。

    高温時と低温時の設定を保持し、それぞれをプロパティとして提供します。
    """

    high_temperature: HighTemperaturePreference
    """高温時の設定"""

    low_temperature: LowTemperaturePreference
    """低温時の設定"""

    solar_utilization:SolarUtilizationPreference
    """太陽光利用"""