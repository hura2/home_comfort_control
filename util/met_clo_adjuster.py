from db.db_session_manager import DBSessionManager
from logger.system_event_logger import SystemEventLogger
from repository.services.weather_forecast_hourly_service import WeatherForecastHourlyService
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
            met_clo_preference.high_temperature.met.sleeping
            if is_sleeping
            else met_clo_preference.high_temperature.met.awake
        )
        clo = (
            met_clo_preference.high_temperature.clo.sleeping
            if is_sleeping
            else met_clo_preference.high_temperature.clo.awake
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
            met_clo_preference.low_temperature.met.sleeping
            if is_sleeping
            else met_clo_preference.low_temperature.met.awake
        )
        clo = (
            met_clo_preference.low_temperature.clo.sleeping
            if is_sleeping
            else met_clo_preference.low_temperature.clo.awake
        )

        if met_clo_preference.low_temperature.time.heating.enabled:
            # 暖房抑制を適用
            now = TimeHelper.get_current_time()
            # 高コスト時間帯でのmet調整
            current_day = now.weekday()
            for period in met_clo_preference.low_temperature.time.heating.high_costs:
                if (current_day not in [5, 6]) and (period.start_time <= now.time() <= period.end_time):
                    met += period.met_adjustment
                    SystemEventLogger.log_info(
                        "icl_adjustment.high_cost",
                        start_time=period.start_time,
                        end_time=period.end_time,
                    )

            # 低コスト時間帯でのmet調整
            for period in met_clo_preference.low_temperature.time.heating.low_costs:
                if (current_day not in [5, 6]) and (period.start_time <= now.time() <= period.end_time):
                    met += period.met_adjustment
                    SystemEventLogger.log_info(
                        "icl_adjustment.low_cost",
                        start_time=period.start_time,
                        end_time=period.end_time,
                    )

        # 太陽光利用
        met = MetCloAdjuster._adjust_for_solar(met)

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
            met_clo_preference.low_temperature.met.sleeping
            if is_sleeping
            else met_clo_preference.low_temperature.met.awake
        )

        clo = (
            max(1.00 - 0.025 * max(min(temperature, 40) - 10, 0), 0.7)
            if not is_sleeping
            # else max(2.0 - 0.06 * max(min(temperature, 15) - 9, 0), 1.2)
            else max(2.0 - 0.10 * max(min(temperature, 15) - 9, 0), 1.2)
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
                met_clo_preference.high_temperature.time.lunch.enabled,
                met_clo_preference.high_temperature.time.lunch.start_time,
                met_clo_preference.high_temperature.time.lunch.end_time,
                met_clo_preference.high_temperature.time.lunch.met_adjustment,
            ),
            (
                met_clo_preference.high_temperature.time.dinner.enabled,
                met_clo_preference.high_temperature.time.dinner.start_time,
                met_clo_preference.high_temperature.time.dinner.end_time,
                met_clo_preference.high_temperature.time.dinner.met_adjustment,
            ),
            (
                met_clo_preference.high_temperature.time.sleep_prep.enabled,
                met_clo_preference.high_temperature.time.sleep_prep.start_time,
                met_clo_preference.high_temperature.time.sleep_prep.end_time,
                met_clo_preference.high_temperature.time.sleep_prep.met_adjustment,
            ),
        ]

        # 各食事時間帯に応じてMETを調整
        for enabled, start, end, adjustment in meal_adjustments:
            if (
                enabled and start <= TimeHelper.get_current_time().time() <= end
            ):  # 設定が有効で、現在の時間帯に該当する場合
                met = round(met + adjustment, 2)  # METを増加

        return met

    @staticmethod
    def _adjust_for_solar(met: float) -> float:
        """
        太陽光利用による暖房抑制を考慮してMET値を調整する。

        Args:
            met (float): 調整前のMET値

        Returns:
            float: 調整後のMET値
        """
        # 現在の日時を取得
        current_time = TimeHelper.get_current_time()

        # 太陽光利用による暖房抑制が有効でない場合は何もせず返す
        if not met_clo_preference.solar_utilization.heating_reduction.enabled:
            return met

        # 現在時刻が暖房抑制の設定時間外である場合は何もせず返す
        heating_reduction = met_clo_preference.solar_utilization.heating_reduction
        if not (heating_reduction.start_time <= current_time.time() <= heating_reduction.end_time):
            return met

        # データベースが無効化されている場合は何もせず返す
        if not app_preference.database.enabled:
            return met

        # 現在時刻を基準に次の時間単位の天気予報を取得
        with DBSessionManager.session() as session:
            weather_service = WeatherForecastHourlyService(session)
            weather_forecast = weather_service.get_closest_future_forecast()

            # 天気予報データが存在する場合に処理を進める
            if weather_forecast:

                # 曇り度が指定された閾値を下回る場合にMET値を調整
                if (
                    weather_forecast.cloud_percentage is not None
                    and weather_forecast.cloud_percentage
                    < heating_reduction.cloudiness_threshold / 100
                ):
                    # 曇り度が閾値を下回ることをログに記録
                    SystemEventLogger.log_solar_utilization_heating_reduction()

                    # 太陽光利用の効果を加味してMET値を調整
                    return met + heating_reduction.met_adjustment

        # デフォルトではMET値をそのまま返す
        return met
