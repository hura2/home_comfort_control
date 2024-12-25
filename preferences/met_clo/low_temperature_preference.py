# ファイル名: low_temperature_preference.py

from pydantic import BaseModel

from preferences.met_clo.clo_preference import CloPreference
from preferences.met_clo.met_preference import MetPreference
from preferences.met_clo.time_period_preference import TimePeriodPreference


class LowTemperaturePreference(BaseModel):
    """
    低温時の設定を管理するクラス。
    
    代謝量、衣服熱抵抗、時間帯の設定を含み、それぞれの設定をプロパティとして提供します。
    """

    met: MetPreference
    """代謝量設定"""

    clo: CloPreference
    """衣服熱抵抗設定"""

    time: "TimePreference"
    """時間帯設定"""

    class TimePreference(BaseModel):
        """時間帯設定を管理するクラス"""

        heating: "HeatingPreference"
        """暖房時の設定"""

        class HeatingPreference(BaseModel):
            """暖房時の設定を管理するクラス"""

            use: bool
            """暖房の使用有無"""

            high_costs: list[TimePeriodPreference]
            """暖房時の高コスト時間帯設定"""

            low_costs: list[TimePeriodPreference]
            """暖房時の低コスト時間帯設定"""