from logger.system_event_logger import SystemEventLogger
from settings import app_preference, met_clo_preference
from shared.dataclass.comfort_factors import ComfortFactors
from util.time_helper import TimeHelper


class MetCloAdjuster:
    """
    気温や時間帯、活動状態に基づいて、快適さに影響を与えるMET（代謝量）とCLO（衣服断熱値）を計算するクラス。

    主な目的:
    - 外気温や最高気温予測に基づいて快適指数を調整。
    - 食事時間帯やコスト時間帯など、特定の条件に応じた調整も実施。
    """

    @staticmethod
    def calculate_comfort_factors(temperature: float, is_sleeping: bool) -> ComfortFactors:
        """
        ComfortFactorsを計算し、返す。

        - 外気温と予測最高気温に基づいて快適性指数を調整。
        - 高温、低温、中間の条件に分類してそれぞれのロジックを適用。

        引数:
            outdoor_temperature (float): 外気温（摂氏）。
            forecast_max_temperature (float): 予報された最高気温（摂氏）。
            is_sleeping (bool): 就寝中かどうかのフラグ。

        戻り値:
            ComfortFactors: METとCLO値を含むインスタンス。
        """
        now = TimeHelper.get_current_time()

        match temperature:
            case temp if temp >= app_preference.temperature_thresholds.high:
                # 高温条件の処理
                return MetCloAdjuster._calculate_high_temp_comfort_factors(is_sleeping)
            case temp if temp <= app_preference.temperature_thresholds.low:
                # 低温条件の処理
                return MetCloAdjuster._calculate_low_temp_comfort_factors(is_sleeping)
            case _:
                # 中間温度条件の処理
                return MetCloAdjuster._calculate_mid_temp_comfort_factors(temperature, is_sleeping)

    @staticmethod
    def _calculate_high_temp_comfort_factors(is_sleeping: bool) -> ComfortFactors:
        """
        高温時のComfortFactorsを計算。

        - 就寝中か活動中かで異なるMET/CLO値を適用。
        - 食事時間帯に応じてMETをさらに調整。

        引数:
            is_sleeping (bool): 就寝中かどうかのフラグ。
            now (datetime): 現在の日時。
            met_clo_config (MetCloConfig): 温度設定のオブジェクト。

        戻り値:
            ComfortFactors: 高温時のMETとCLOを含むインスタンス。
        """
        met = (
            met_clo_preference.high_temperature.met.bedtime
            if is_sleeping
            else met_clo_preference.high_temperature.met.daytime
        )
        clo = (
            met_clo_preference.high_temperature.clo.bedtime
            if is_sleeping
            else met_clo_preference.high_temperature.clo.daytime
        )

        # 食事時間帯によるMETの調整を実施
        met = MetCloAdjuster.adjust_met_for_meal_times(met)
        return ComfortFactors(met=met, clo=clo)

    @staticmethod
    def _calculate_low_temp_comfort_factors(is_sleeping: bool) -> ComfortFactors:
        """
        低温時のComfortFactorsを計算。

        - 低温環境での快適性を向上させるため、コスト時間帯でMETを調整。
        - 就寝中か活動中かでCLO値を切り替え。

        引数:
            is_sleeping (bool): 就寝中かどうかのフラグ。
            now (datetime): 現在の日時。
            settings (MetCloConfig): 温度設定。

        戻り値:
            ComfortFactors: METとCLO値を含むインスタンス。
        """
        met = (
            met_clo_preference.low_temperature.met.bedtime
            if is_sleeping
            else met_clo_preference.low_temperature.met.daytime
        )
        clo = (
            met_clo_preference.low_temperature.clo.bedtime
            if is_sleeping
            else met_clo_preference.low_temperature.clo.daytime
        )

        now = TimeHelper.get_current_time()
        # 高コスト時間帯でのmet調整
        current_day = now.weekday()
        for period in met_clo_preference.low_temperature.time.heating.high_costs:
            if (current_day not in [5, 6]) and (period.start <= now.time() <= period.end):
                met += period.met_adjustment
                SystemEventLogger.log_info(
                    "icl_adjustment.high_cost",
                    start_time=period.start,
                    end_time=period.end,
                )

        # 低コスト時間帯でのmet調整
        for period in met_clo_preference.low_temperature.time.heating.low_costs:
            if (current_day not in [5, 6]) and (period.start <= now.time() <= period.end):
                met += period.met_adjustment
                SystemEventLogger.log_info(
                    "icl_adjustment.low_cost",
                    start_time=period.start,
                    end_time=period.end,
                )

        return ComfortFactors(met=met, clo=clo)

    @staticmethod
    def _calculate_mid_temp_comfort_factors(
        temperature: float, is_sleeping: bool
    ) -> ComfortFactors:
        """
        中間温度時のComfortFactorsを計算。

        - 外気温と予測最高気温の平均を基にMET/CLO値を調整。
        - 就寝中か活動中かで異なるCLO値を適用。

        引数:
            outdoor_temperature (float): 外気温（摂氏）。
            forecast_max_temperature (float): 予報された最高気温（摂氏）。
            is_sleeping (bool): 就寝中かどうかのフラグ。
            settings (MetCloConfig): 温度設定。

        戻り値:
            ComfortFactors: METとCLO値を含むインスタンス。
        """
        met = (
            met_clo_preference.low_temperature.met.bedtime
            if is_sleeping
            else met_clo_preference.low_temperature.met.daytime
        )

        clo = (
            max(1.00 - 0.025 * max(min(temperature, 40) - 10, 0), 0.7)
            if not is_sleeping
            else max(2.0 - 0.06 * max(min(temperature, 15) - 9, 0), 1.2)
        )

        return ComfortFactors(met=met, clo=clo)

    @staticmethod
    def adjust_met_for_meal_times(met: float) -> float:
        """
        食事時間帯によるMETの調整を行う。

        引数:
            met (float): 現在のMET値。
            now(datetime): 現在の日時。
            met_clo_config(MetCloConfig): 温度設定のオブジェクト。

        戻り値:
            float: 調整されたMET値。
        """
        # 食事時間帯の調整設定
        meal_adjustments = [
            (
                met_clo_preference.high_temperature.time.lunch_time.use,
                met_clo_preference.high_temperature.time.lunch_time.start,
                met_clo_preference.high_temperature.time.lunch_time.end,
                met_clo_preference.high_temperature.time.lunch_time.met_adjustment,
            ),
            (
                met_clo_preference.high_temperature.time.dinner_time.use,
                met_clo_preference.high_temperature.time.dinner_time.start,
                met_clo_preference.high_temperature.time.dinner_time.end,
                met_clo_preference.high_temperature.time.dinner_time.met_adjustment,
            ),
            (
                met_clo_preference.high_temperature.time.pre_bedtime.use,
                met_clo_preference.high_temperature.time.pre_bedtime.start,
                met_clo_preference.high_temperature.time.pre_bedtime.end,
                met_clo_preference.high_temperature.time.pre_bedtime.met_adjustment,
            ),
        ]

        # 各食事時間帯に応じてMETを調整
        for use, start, end, adjustment in meal_adjustments:
            if (
                use and start <= TimeHelper.get_current_time().time() <= end
            ):  # 設定が有効で、現在の時間帯に該当する場合
                met = round(met + adjustment, 2)  # METを増加

        return met
