# ファイル名: high_temperature_preference.py

from pydantic import BaseModel

from preferences.met_clo.clo_preference import CloPreference
from preferences.met_clo.met_preference import MetPreference
from preferences.met_clo.time_period_preference import TimePeriodPreference


class HighTemperaturePreference(BaseModel):
    """
    高温時の設定を管理するクラス。

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

        lunch: TimePeriodPreference
        """昼食時間帯の設定"""

        dinner: TimePeriodPreference
        """夕食時間帯の設定"""

        sleep_prep: TimePeriodPreference
        """就寝前の時間帯設定"""
