from datetime import datetime

from settings.clothing_activity_by_temperature_settings import ClothingActivityByTemperatureSettings
from settings.general_settings import GeneralSettings
from util.time import TimeUtil


class ClothingActivityByTemperatureCalculator:
    """
    外気温、最高気温、および就寝状況に基づき、適切なMET（代謝当量）とICL（快適さ指標）を計算するクラス。

    このクラスは、高温、低温、および中間温度の3つの温度範囲に応じて処理を分岐し、各温度範囲における
    活動や服装の設定に基づきMETおよびICLを計算します。また、食事時間帯や電気代の高い時間帯の調整も行います。

    主なメソッド:
        - calculate_met_icl: 外気温、最高気温、および就寝状況を入力としてMETとICLを計算するメソッド。
        - calculate_high_temp_met_icl: 高温時のMETとICLを計算するための内部メソッド。
        - calculate_low_temp_met_icl: 低温時のMETとICLを計算するための内部メソッド。
        - calculate_mid_temp_met_icl: 中間温度時のMETとICLを計算するための内部メソッド。
        - adjust_met_for_meal_times: 昼食や夕食など、特定の時間帯に応じてMETを調整するための内部メソッド。

    使用方法:
        本クラスはすべてのメソッドを `@staticmethod` として定義しており、インスタンス化せずに直接呼び出すことが可能です。
        例えば、`ClothingActivityByTemperatureCalculator.calculate_met_icl(outdoor_temperature, max_temp, bedtime)` のように利用します。

    例:
        outdoor_temperature = 30.0
        max_temp = 35
        bedtime = False
        met, icl = ClothingActivityByTemperatureCalculator.calculate_met_icl(outdoor_temperature, max_temp, bedtime)

    """


from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass
class ComfortFactors:
    """快適さの要因を保持するクラス。MET（代謝当量）とICL（衣服断熱）を含む。"""

    met: float
    icl: float


class ClothingActivityByTemperatureCalculator:
    @staticmethod
    def calculate_comfort_factors(
        outdoor_or_forecast_temperature: float, forecast_max_temperature: int, is_sleeping: bool
    ) -> ComfortFactors:
        """
        METとICLを計算し、ComfortFactorsとして返す関数。

        外気温、最高気温、就寝中かどうかを基にMETとICLを計算します。
        食事時間帯や電気代高騰の時間帯も考慮しています。

        引数:
            outdoor_or_forecast_temperature (float): 外気温（摂氏）。
            forecast_max_temperature (int): 予報された最高気温（摂氏）。
            is_sleeping (bool): 就寝中かどうかのフラグ。

        戻り値:
            ComfortFactors: 計算されたMETとICLの値。
        """
        now = TimeUtil.get_current_time()
        settings = GeneralSettings()
        cat_settings = ClothingActivityByTemperatureSettings()

        # 高温、低温、中間の条件に応じてComfortFactorsを取得
        if forecast_max_temperature >= settings.temperature_thresholds.high_temperature_threshold:
            return ClothingActivityByTemperatureCalculator._calculate_high_temp_comfort_factors(
                is_sleeping, now, cat_settings
            )
        elif forecast_max_temperature <= settings.temperature_thresholds.low_temperature_threshold:
            return ClothingActivityByTemperatureCalculator._calculate_low_temp_comfort_factors(
                is_sleeping, now, cat_settings
            )
        else:
            return ClothingActivityByTemperatureCalculator._calculate_mid_temp_comfort_factors(
                outdoor_or_forecast_temperature, is_sleeping, cat_settings
            )

    @staticmethod
    def _calculate_high_temp_comfort_factors(
        is_sleeping: bool, now: datetime, settings: ClothingActivityByTemperatureSettings
    ) -> ComfortFactors:
        """高温時のComfortFactorsを計算し、返す。

        引数:
            is_sleeping (bool): 就寝中かどうかのフラグ。
            now (datetime): 現在の日時。
            settings (ClothingActivityByTemperatureSettings): 温度設定。

        戻り値:
            ComfortFactors: 高温時のMETとICLを含むComfortFactorsインスタンス。
        """
        met = settings.high_temp_settings.met.bedtime if is_sleeping else settings.high_temp_settings.met.daytime
        icl = settings.high_temp_settings.icl.bedtime if is_sleeping else settings.high_temp_settings.icl.daytime

        # 食事時間帯の調整
        met = ClothingActivityByTemperatureCalculator.adjust_met_for_meal_times(met, now, settings)
        return ComfortFactors(met=met, icl=icl)

    @staticmethod
    def _calculate_low_temp_comfort_factors(
        is_sleeping: bool, now: datetime, settings: ClothingActivityByTemperatureSettings
    ) -> ComfortFactors:
        """低温時のComfortFactorsを計算し、返す。

        引数:
            is_sleeping (bool): 就寝中かどうかのフラグ。
            now (datetime): 現在の日時。
            settings (ClothingActivityByTemperatureSettings): 温度設定。

        戻り値:
            ComfortFactors: 低温時のMETとICLを含むComfortFactorsインスタンス。
        """
        met = settings.low_temp_settings.met.bedtime if is_sleeping else settings.low_temp_settings.met.daytime
        icl = settings.low_temp_settings.icl.bedtime if is_sleeping else settings.low_temp_settings.icl.daytime

        # 高コスト時間帯でのICL調整
        current_day = now.weekday()
        if (current_day not in [5, 6]) and (
            settings.low_temp_settings.time_settings.heating.high_cost.start
            <= now.time()
            <= settings.low_temp_settings.time_settings.heating.high_cost.end
        ):
            icl += settings.low_temp_settings.time_settings.heating.high_cost.adjustment

        # 低コスト時間帯でのICL調整
        if (current_day not in [5, 6]) and (
            settings.low_temp_settings.time_settings.heating.low_cost.start
            <= now.time()
            <= settings.low_temp_settings.time_settings.heating.low_cost.end
        ):
            icl += settings.low_temp_settings.time_settings.heating.low_cost.adjustment

        return ComfortFactors(met=met, icl=icl)

    @staticmethod
    def _calculate_mid_temp_comfort_factors(
        outdoor_temperature: float, is_sleeping: bool, settings: ClothingActivityByTemperatureSettings
    ) -> ComfortFactors:
        """中間温度時のComfortFactorsを計算し、返す。

        引数:
            outdoor_temperature (float): 外気温（摂氏）。
            is_sleeping (bool): 就寝中かどうかのフラグ。
            settings (ClothingActivityByTemperatureSettings): 温度設定。

        戻り値:
            ComfortFactors: 中間温度時のMETとICLを含むComfortFactorsインスタンス。
        """
        met = settings.low_temp_settings.met.bedtime if is_sleeping else settings.low_temp_settings.met.daytime
        icl = (
            max(1.00 - 0.025 * max(min(outdoor_temperature, 40) - 10, 0), 0.6)
            if not is_sleeping
            else max(2.0 - 0.06 * max(min(outdoor_temperature, 15) - 9, 0), 1.2)
        )

        return ComfortFactors(met=met, icl=icl)

    @staticmethod
    def adjust_met_for_meal_times(met: float, now: datetime, settings: ClothingActivityByTemperatureSettings) -> float:
        """食事時間帯によるMETの調整を行う。

        引数:
            met (float): 現在のMET値。
            now(datetime): 現在の日時。
            settings(ClothingActivityByTemperatureSettings): 温度設定のオブジェクト。

        戻り値:
            float: 調整されたMET値。
        """
        # 食事時間帯の調整設定
        meal_adjustments = [
            (
                settings.high_temp_settings.time_settings.lunch_time.use,
                settings.high_temp_settings.time_settings.lunch_time.start,
                settings.high_temp_settings.time_settings.lunch_time.end,
                settings.high_temp_settings.time_settings.lunch_time.met,
            ),
            (
                settings.high_temp_settings.time_settings.dinner_time.use,
                settings.high_temp_settings.time_settings.dinner_time.start,
                settings.high_temp_settings.time_settings.dinner_time.end,
                settings.high_temp_settings.time_settings.dinner_time.met,
            ),
            (
                settings.high_temp_settings.time_settings.pre_bedtime.use,
                settings.high_temp_settings.time_settings.pre_bedtime.start,
                settings.high_temp_settings.time_settings.pre_bedtime.end,
                settings.high_temp_settings.time_settings.pre_bedtime.met,
            ),
        ]

        # 各食事時間帯に応じてMETを調整
        for use, start, end, adjustment in meal_adjustments:
            if use and start <= now.time() <= end:  # 設定が有効で、現在の時間帯に該当する場合
                met = round(met + adjustment, 2) # METを増加

        return met
