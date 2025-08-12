from logger.system_event_logger import SystemEventLogger
from models.weather_forecast_hourly_model import WeatherForecastHourlyModel
from preferences.aircon.conditional_aircon_preference import ConditionalAirconPreference
from preferences.aircon.conditional_preference import SummerCondensationPreference
from settings import aircon_preference, app_preference
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.pmv_result import PMVResult
from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from util.time_helper import TimeHelper
from util.weekday_helper import WeekdayHelper


class AirconSettingsDeterminer:
    """
    エアコンの設定を決定するクラス
    """

    # エアコンの動作を設定する関数
    @staticmethod
    def determine_aircon_settings(
        pmvResult: PMVResult,
        home_sensor: HomeSensor,
        closest_future_forecast: WeatherForecastHourlyModel | None,
        is_sleeping: bool,
    ) -> AirconSettings:
        """
        エアコンの設定を決定するメソッド
        Args:
            pmvResult (PMVResult): PMV計算結果を持つオブジェクト。
            home_sensor (HomeSensor): 家庭の環境情報を格納したオブジェクト。
            closest_future_forecast (WeatherForecastHourlyModel | None): 最も近い未来の天気予報。
            is_sleeping (bool): 寝ている時間。
        Returns:
            AirconSettings: 設定されたエアコンの設定。
        """
        # エアコンの設定をPMVを元にひとまず決定
        aircon_settings = AirconSettingsDeterminer._get_aircon_settings_for_pmv(pmvResult.pmv)
        # 特殊な条件によるエアコン設定を適用
        aircon_settings = AirconSettingsDeterminer._get_aircon_settings_for_conditions(
            aircon_settings, pmvResult, home_sensor, closest_future_forecast, is_sleeping
        )
        return aircon_settings

    # pmvによってエアコンの設定を判定
    @staticmethod
    def _get_aircon_settings_for_pmv(pmv: float) -> AirconSettings:
        """
        pmvによってエアコンの設定を判定するメソッド
        Args:
            pmv (float): PMV値。
        Returns:
            AirconSettings: 設定されたエアコンの設定。
        """

        aircon_settings = AirconSettings()

        # pmvによってエアコンの設定を判定
        found_threshold = False  # 条件を満たすデータが見つかったかどうか

        for pmv_threshold in aircon_preference.aircon_settings.pmv_thresholds:
            if pmv <= pmv_threshold.threshold:
                # 設定を一括で更新
                aircon_settings.update_if_none(pmv_threshold.aircon_settings)
                found_threshold = True  # 条件を満たすデータが見つかった
                break

        # 条件を満たすデータがなかった場合、最後の要素の設定を使用
        if not found_threshold and aircon_preference.aircon_settings.pmv_thresholds:
            last_threshold = aircon_preference.aircon_settings.pmv_thresholds[-1]
            aircon_settings.update_if_none(last_threshold.aircon_settings)

        return aircon_settings

    @staticmethod
    def _should_turn_off_cooling(
        pmv_result: PMVResult,
        outdoor_temperature: float,
        cooling_preference: ConditionalAirconPreference,
    ) -> bool:
        """
        冷房を停止すべきかを判定するメソッド。
        PMV（Predicted Mean Vote）値と外気温を基に、冷房の停止を判断します。

        判定基準:
        - PMVが閾値未満であり、屋外温度との差が屋内温度より低ければ冷房停止
        - 屋外温度がアプリケーション設定で定義された最低温度閾値を下回った場合
        """
        return (
            # 外気温との差が屋内温度より大きい場合、冷房を停止する
            pmv_result.mean_radiant_temperature
            - cooling_preference.activation.outdoor_temperature_diff
            > outdoor_temperature
            # さらにPMVが設定閾値を下回るとき
            and pmv_result.pmv < cooling_preference.activation.threshold
        ) or outdoor_temperature < app_preference.temperature_thresholds.low
        # もしくは、外気温が設定した低温閾値より低ければ冷房を停止

    @staticmethod
    def _should_turn_off_heating(
        pmv_result: PMVResult,
        outdoor_temperature: float,
        heating_preference: ConditionalAirconPreference,
    ):
        """
        暖房を停止すべきかを判定するメソッド。
        PMV値と外気温を基に、暖房の停止を判断します。

        判定基準:
        - PMVが閾値を超え、屋外温度との差が屋内温度より高い場合、暖房停止
        - 屋外温度がアプリケーション設定で定義された最高温度閾値を上回った場合
        """
        return (
            # 外気温との差が屋内温度より小さい場合、暖房を停止する
            pmv_result.mean_radiant_temperature
            - heating_preference.activation.outdoor_temperature_diff
            < outdoor_temperature
            # さらにPMVが設定閾値を上回るとき
            and pmv_result.pmv > heating_preference.activation.threshold
        ) or outdoor_temperature > app_preference.temperature_thresholds.high
        # もしくは、外気温が設定した高温閾値より高ければ暖房を停止

    @staticmethod
    def _adjust_for_dew_point(
        pmv_result: PMVResult,
        home_sensor: HomeSensor,
        aircon_settings: AirconSettings,
        summer_condensation_pref: SummerCondensationPreference,
    ):
        """
        室内温度と露点温度に基づいてエアコン設定を調整するメソッド。
        室内温度が露点温度以下になると、エアコン設定を変更する。
        """
        if (
            # 室内温度が露点温度より低い場合（露点以下）
            home_sensor.main.air_quality.temperature
            < home_sensor.indoor_dew_point - summer_condensation_pref.dew_point_margin
        ):
            # PMV値が指定されたしきい値を超えるとき、露点に関する設定をオーバーライド
            if pmv_result.pmv > summer_condensation_pref.pmv_threshold:
                SystemEventLogger.log_info(
                    "aircon_related.indoor_temp_below_dewpoint_high_pmv", pmv=pmv_result.pmv
                )
                # 露点に関してエアコン設定を更新
                aircon_settings.update_if_none(
                    summer_condensation_pref.condensation_override.aircon_settings
                )
                # 強制的にファンを動作させる
                aircon_settings.force_fan_below_dew_point = True
            else:
                # PMV値がしきい値以下の場合、標準的な冷房設定を適用
                SystemEventLogger.log_info("aircon_related.indoor_temp_below_dewpoint")
                aircon_settings.update_if_none(
                    summer_condensation_pref.cooling_stop.aircon_settings
                )
                aircon_settings.force_fan_below_dew_point = True

    @staticmethod
    def _adjust_for_humidity(home_sensor: HomeSensor, aircon_settings: AirconSettings):
        """
        室内の絶対湿度に基づいてエアコン設定を調整するメソッド。
        湿度がしきい値を超えると、除湿モードを適用する。
        """
        if aircon_settings.mode.is_cooling():
            return
        
        if (
            # 室内の絶対湿度が設定されたしきい値を超える場合
            home_sensor.average_indoor_absolute_humidity
            > app_preference.environment.dehumidification_threshold
        ):
            SystemEventLogger.log_info(
                "humidity_related.absolute_humidity_threshold_exceeded",
                threshold=app_preference.environment.dehumidification_threshold,
            )
            # しきい値を超えた場合、エアコン設定を除湿モードに更新
            aircon_settings.update_if_none(aircon_preference.aircon_settings.dry.aircon_settings)

    @staticmethod
    def _adjust_for_co2(home_sensor: HomeSensor, aircon_settings: AirconSettings):
        """
        CO2濃度に基づいてエアコンの風量を調整するメソッド。
        CO2濃度がしきい値を超えると風量を強くする。
        """
        if home_sensor.main_co2_level is not None:
            # CO2濃度が警告しきい値を超えた場合
            if home_sensor.main_co2_level > app_preference.co2_thresholds.warning:
                aircon_settings.fan_speed = AirconFanSpeed.HIGH
            # しきい値を超える場合、風量を中程度に設定
            elif home_sensor.main_co2_level > app_preference.co2_thresholds.high:
                aircon_settings.fan_speed = AirconFanSpeed.MEDIUM

    @staticmethod
    def _adjust_for_temperature_difference(
        home_sensor: HomeSensor,
        aircon_settings: AirconSettings,
        is_sleeping: bool,
        circulator_threshold: float,
    ):
        """
        部屋間の温度差に基づいて風量を調整するメソッド。
        寝ていない時に部屋間の温度差が設定閾値を超えると風量を強くする。
        """
        # 最大の温度差を取得
        max_diff_value = max(
            abs(home_sensor.main.air_quality.temperature - sup.air_quality.temperature)
            for sup in home_sensor.supplementaries
        )
        # 寝ていない場合で、温度差が閾値を超えたら
        if not is_sleeping and max_diff_value > circulator_threshold:
            SystemEventLogger.log_info(
                "aircon_related.room_temp_diff_high", temp_diff=circulator_threshold
            )
            # 風量を強く設定
            aircon_settings.fan_speed = AirconFanSpeed.HIGH

    @staticmethod
    def _get_aircon_settings_for_conditions(
        aircon_settings: AirconSettings,
        pmv_result: PMVResult,
        home_sensor: HomeSensor,
        closest_future_forecast: WeatherForecastHourlyModel | None,
        is_sleeping: bool,
    ) -> AirconSettings:
        """
        各種環境条件に基づき、エアコンの設定を調整するメソッド。

        主な処理内容:
            1. 外気温に基づく冷暖房の停止判定
            2. 快適管理（湿度・CO₂）や太陽光パネル状態に基づく制御
            3. 湿度・CO₂・温度差・露点などの条件に応じた細かい設定調整

        引数:
            aircon_settings: 現在のエアコン設定
            pmv_result: PMV（Predicted Mean Vote）計算結果
            home_sensor: 室内・室外センサーの測定値
            closest_future_forecast: 直近の予報データ（天気・曇り度など）
            is_sleeping: 睡眠中かどうかのフラグ

        戻り値:
            調整後のエアコン設定
        """

        # --- 1. 外気温に基づく冷暖房の停止判定 ---
        if home_sensor.outdoor:
            # 冷房モードの場合
            if aircon_settings.mode.is_cooling():
                # 外気温・PMVに基づき冷房停止すべきか判定
                if AirconSettingsDeterminer._should_turn_off_cooling(
                    pmv_result,
                    home_sensor.outdoor.air_quality.temperature,
                    aircon_preference.conditional.cooling,
                ):
                    # 冷房停止用設定に更新（風量・温度・モードなどをオフ状態へ）
                    aircon_settings.update_if_none(
                        aircon_preference.conditional.cooling.off_state.aircon_settings
                    )
                    SystemEventLogger.log_info(
                        "outdoor_temperature_related.wait_for_natural_heating"
                    )

            # 暖房モードの場合
            if aircon_settings.mode.is_heating():
                # 外気温・PMVに基づき暖房停止すべきか判定
                if AirconSettingsDeterminer._should_turn_off_heating(
                    pmv_result,
                    home_sensor.outdoor.air_quality.temperature,
                    aircon_preference.conditional.heating,
                ):
                    # 暖房停止用設定に更新
                    aircon_settings.update_if_none(
                        aircon_preference.conditional.heating.off_state.aircon_settings
                    )
                    SystemEventLogger.log_info(
                        "outdoor_temperature_related.wait_for_natural_cooling"
                    )

        # --- 2. 快適管理および太陽光パネルによる制御 ---
        if AirconSettingsDeterminer._is_comfort_control_disabled():
            # 湿度・CO₂の快適管理は有効だが温度制御は行わない場合
            if app_preference.comfort_control.environment_control_enabled:
                SystemEventLogger.log_info("comfort_control_disabled.environment_control_enabled")
                # 温度制御系の運転モード（冷房・暖房）は停止
                if aircon_settings.mode.is_cooling() or aircon_settings.mode.is_heating():
                    aircon_settings.update_if_none(
                        aircon_preference.conditional.cooling.off_state.aircon_settings
                    )
            else:
                # 湿度・CO₂の快適管理も無効な場合は太陽光制御を確認
                if not AirconSettingsDeterminer._is_solar_control_available(closest_future_forecast):
                    # 太陽光制御が無効なら運転停止
                    aircon_settings.update_if_none(
                        aircon_preference.conditional.cooling.off_state.aircon_settings
                    )
                    return aircon_settings  # 以降の調整処理は行わず終了

        # --- 3. その他の環境要因による微調整 ---
        # 湿度条件に応じた調整
        AirconSettingsDeterminer._adjust_for_humidity(home_sensor, aircon_settings)

        # CO₂濃度条件に応じた調整
        AirconSettingsDeterminer._adjust_for_co2(home_sensor, aircon_settings)

        # 室内外の温度差に応じたサーキュレーター運転調整（特に睡眠中に配慮）
        AirconSettingsDeterminer._adjust_for_temperature_difference(
            home_sensor,
            aircon_settings,
            is_sleeping,
            aircon_preference.conditional.circulator_threshold,
        )

        # 露点温度に応じた結露防止調整（夏期など）
        AirconSettingsDeterminer._adjust_for_dew_point(
            pmv_result,
            home_sensor,
            aircon_settings,
            aircon_preference.conditional.summer_condensation,
        )

        return aircon_settings


    @staticmethod
    def _is_comfort_control_disabled() -> bool:
        """
        現在の時刻が、設定された無効期間に該当するかを判定します。

        Returns:
            True: 操作を無効化（スキップ）すべき場合
            False: 通常通り操作を行うべき場合
        """
        # 曜日を日本語で取得
        current_datetime = TimeHelper.get_current_time()
        current_time = current_datetime.time()

        for period in app_preference.comfort_control.disabled_periods:
            # 現在の曜日と一致するか確認
            if period.day == current_datetime.weekday():
                # timesがNoneの場合、終日無効と判断
                if period.times is None or len(period.times) == 0:
                    SystemEventLogger.log_info(
                        "comfort_control_disabled.all_day",
                        weekday=WeekdayHelper.index_to_name(period.day),
                    )
                    return True

                # timesがリストで、空ではない場合
                if period.times:
                    for time_range in period.times:
                        # 現在時刻が時間帯の範囲内か判定
                        if time_range.start_time <= current_time < time_range.end_time:
                            SystemEventLogger.log_info(
                                "comfort_control_disabled.specific_period",
                                weekday=WeekdayHelper.index_to_name(period.day),
                                start_time=time_range.start_time,
                                end_time=time_range.end_time,
                            )
                            return True

                # timesが空リストの場合は、その曜日は無効時間帯がないため、処理を継続
                return False

        # どの無効期間にも該当しない場合
        return False
    
    @staticmethod
    def _is_solar_control_available(closest_future_forecast: WeatherForecastHourlyModel | None) -> bool:
        """
        太陽光パネルによる快適管理が有効かどうかを判定する。

        戻り値:
            True  -> 太陽光パネルによる制御を行える状態
            False -> 太陽光パネルによる制御が行えない状態（無効）
        """
        # 太陽光パネル機能がOFFの場合は無効
        if not app_preference.comfort_control.solar_panel_enabled:
            return False

        SystemEventLogger.log_info("comfort_control_disabled.solar_panel_enabled")

        # 現在時刻と有効時間帯のチェック
        current_time = TimeHelper.get_current_time().time()
        active_hours = app_preference.comfort_control.solar_active_hours
        if not (active_hours.start_time <= current_time <= active_hours.end_time):
            return False

        SystemEventLogger.log_info(
            "comfort_control_disabled.solar_active_hours",
            start_time=active_hours.start_time,
            end_time=active_hours.end_time,
        )

        # 曇り度チェック（閾値未満なら有効）
        cloud_threshold = app_preference.comfort_control.solar_cloud_threshold
        if (
            closest_future_forecast is None
            or closest_future_forecast.cloud_percentage is None
            or closest_future_forecast.cloud_percentage >= cloud_threshold * 0.01
        ):
            SystemEventLogger.log_info(
                "comfort_control_disabled.solar_cloud_threshold_disable",
                threshold=cloud_threshold,
            )
            return False

        SystemEventLogger.log_info(
            "comfort_control_disabled.solar_cloud_threshold",
            threshold=cloud_threshold,
        )
        return True

