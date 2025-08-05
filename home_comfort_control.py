import datetime

from api.smart_home_devices.smart_home_device_factory import SmartHomeDeviceFactory
from api.weather_foreecast.weather_forecast_factory import WeatherForecastFactory
from db.db_session_manager import DBSessionManager
from devices.aircon.aircon_operation import AirconOperation
from devices.aircon.aircon_settings_determiner import AirconSettingsDeterminer
from devices.aircon.aircon_state_manager import AirconStateManager
from devices.circulator import Circulator
from logger.system_event_logger import SystemEventLogger
from models.weather_forecast_hourly_model import WeatherForecastHourlyModel
from repository.services.aircon_change_intarval_service import AirconChangeIntarvalService
from repository.services.aircon_intensity_score_service import AirconIntensityScoreService
from repository.services.aircon_setting_service import AirconSettingService
from repository.services.circulator_setting_service import CirculatorSettingService
from repository.services.measurement_service import MeasurementService
from repository.services.weather_forecast_hourly_service import WeatherForecastHourlyService
from repository.services.weather_forecast_service import WeatherForecastService
from settings import LOCAL_TZ, aircon_preference, app_preference
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.dataclass.comfort_factors import ComfortFactors
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.pmv_result import PMVResult
from shared.enums.power_mode import PowerMode
from util.thermal_comfort import ThermalComfort
from util.time_helper import TimeHelper
from util.weekday_helper import WeekdayHelper


class HomeComfortControl:
    """家の快適環境を制御するクラス"""

    def initialize_home_sensor(self) -> HomeSensor:
        """
        センサー情報を取得する
        Returns:
            HomeSensor: センサー情報
        """
        # センサー情報を取得
        home_sensor = HomeSensor(
            main=app_preference.sensors.main,
            sub=app_preference.sensors.sub,
            supplementaries=app_preference.sensors.supplementaries,
            outdoor=app_preference.sensors.outdoor,
        )
        smart_home_device = SmartHomeDeviceFactory.create_device()

        # mainセンサーの空気質情報を取得
        home_sensor.main.air_quality = smart_home_device.get_air_quality_by_sensor(
            app_preference.sensors.main
        )
        # subセンサーの設定がある場合、subセンサーの空気質情報を取得
        if home_sensor.sub:
            home_sensor.sub.air_quality = smart_home_device.get_air_quality_by_sensor(
                app_preference.sensors.sub
            )
        # supplementariesセンサーの設定がある場合、supplementariesセンサーの空気質情報を取得
        if home_sensor.supplementaries:
            for supplementary in home_sensor.supplementaries:
                supplementary.air_quality = smart_home_device.get_air_quality_by_sensor(
                    supplementary
                )
        # outdoorセンサーの設定がある場合、outdoorセンサーの空気質情報を取得
        if home_sensor.outdoor:
            home_sensor.outdoor.air_quality = smart_home_device.get_air_quality_by_sensor(
                home_sensor.outdoor
            )
        return home_sensor

    def fetch_forecast(self):
        if app_preference.database.enabled == False:
            return

        with DBSessionManager.auto_commit_session() as session:
            weather_forecast_service = WeatherForecastService(session)
            today = TimeHelper.get_current_time()
            # 今日、明日、明後日のデータをアップサート
            weather_forecast_service.upsert_with_hourly(today)

    def fetch_forecast_max_temperature(self) -> float | None:
        """天気予報の最高気温を取得する
        Returns:
            int: 最高気温
        """
        forecast_max_temperature = None
        # データベースを使用する場合
        if app_preference.database.enabled:
            # データベースに保存されている最高気温を取得
            with DBSessionManager.session() as session:
                weather_forecast_service = WeatherForecastService(session)
                forecast_max_temperature = weather_forecast_service.get_max_temperature()
        else:
            # データベースを使用しない場合は、現在の最高気温を取得
            weather_forecast = WeatherForecastFactory().create_forecast()
            weather_date_list = weather_forecast.fetch_forecast(
                TimeHelper.get_current_time().date()
            )
            if weather_date_list and len(weather_date_list) > 0:
                forecast_max_temperature = weather_date_list[0].max_temperature

        return forecast_max_temperature

    def is_within_sleeping_period(self) -> bool:
        """現在の時刻が就寝時間内かどうかをチェックする
        Args:
            now (datetime.datetime): 現在時刻
        Returns:
            bool: 就寝時間内ならTrue、それ以外ならFalse
        """
        now = TimeHelper.get_current_time()
        if now.date().weekday() < 5:  # 土曜(5)または日曜(6)を休日と判定
            # 起床時間を取得
            awake_period_start = LOCAL_TZ.localize(
                datetime.datetime.combine(
                    now.date(), app_preference.weekday_awake_period.start_time
                )
            )
            # 就寝時間を取得
            awake_period_end = LOCAL_TZ.localize(
                datetime.datetime.combine(now.date(), app_preference.weekday_awake_period.end_time)
            )
        else:
            # 起床時間を取得
            awake_period_start = LOCAL_TZ.localize(
                datetime.datetime.combine(
                    now.date(), app_preference.weekend_awake_period.start_time
                )
            )
            # 就寝時間を取得
            awake_period_end = LOCAL_TZ.localize(
                datetime.datetime.combine(now.date(), app_preference.weekend_awake_period.end_time)
            )

        # 就寝中かどうかを判断（起床時間内ならFalse、それ以外ならTrue）
        return awake_period_start > now or awake_period_end < now

    def activate_circulator_in_heat_conditions(
        self, home_sensor: HomeSensor, pmv: float, outdoor_temperature: float
    ) -> CirculatorSettings:
        """
        熱中症の場合、サーキュレーターをオンにする
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv (float): PMV値
            outdoor_temperature (float): 外気温度
        Returns:
            CirculatorSettings: サーキュレーターの状態
        """
        # サーキュレーター使用設定が有効かどうかを確認
        if app_preference.circulator.enabled:
            # サーキュレーターの状態を設定
            circulator_settings = Circulator.set_circulator_by_temperature(
                pmv, home_sensor.average_indoor_absolute_humidity, outdoor_temperature
            )
        return circulator_settings

    def recalculate_pmv_with_circulator(
        self,
        home_sensor: HomeSensor,
        forecast_max_temperature: float,
        circulator_settings: CirculatorSettings,
        comfort_factors: ComfortFactors,
    ) -> PMVResult | None:
        """
        PMV値を再計算する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            forecast_max_temperature (int): 最高気温予報
            circulator_settings (CirculatorSettings): サーキュレーターの状態
            comfort_factors (ComfortFactors): コンフォーマンス因子の値
        Returns:
            PMVResults: PMV計算結果
        """
        pmv = None
        # サーキュレーター使用設定が有効かどうかを確認
        if app_preference.circulator.enabled:
            # サーキュレーターをオンにしている場合、風量を増やしてPMV値を再計算
            if circulator_settings.power == PowerMode.ON:
                pmv = ThermalComfort.calculate_pmv(
                    home_sensor, forecast_max_temperature, comfort_factors, wind_speed=0.3
                )

        return pmv

    def update_aircon_settings(
        self,
        home_sensor: HomeSensor,
        pmv_result: PMVResult,
        outdoor_temperature: float,
        closest_future_forecast: WeatherForecastHourlyModel | None,
        is_sleeping: bool,
    ) -> AirconSettings:
        """
        エアコンの状態を更新する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv_result (PMVResults): PMV計算結果
            outdoor_temperature (float): 外気温度
            closest_future_forecast (WeatherForecastHourlyModel | None): 最も近い未来の天気予報
            is_sleeping (bool): 寝ている時間
        """

        # 現在が快適管理の無効期間（曜日・時間帯）かどうかを判定
        if self.is_comfort_control_disabled():
            # 無効期間の場合は、まず事前に設定されたエアコンのオフ状態の設定を適用する
            aircon_settings = aircon_preference.conditional.cooling.off_state.aircon_settings

            # ただし太陽光パネルが有効ならば、現在時刻と曇り度をチェックして調整を行う
            if app_preference.comfort_control.solar_panel_enabled:
                SystemEventLogger.log_info("comfort_control_disabled.solar_panel_enabled")
                current_time = TimeHelper.get_current_time().time()  # 現在の時刻を取得
                active_hours = (
                    app_preference.comfort_control.solar_active_hours
                )  # 太陽光パネルの有効時間帯を取得
                # 現在時刻が太陽光パネルの有効時間帯内かどうか確認
                if active_hours.start_time <= current_time <= active_hours.end_time:
                    SystemEventLogger.log_info(
                        "comfort_control_disabled.solar_active_hours",
                        start_time=active_hours.start_time,
                        end_time=active_hours.end_time,
                    )
                    # 予報情報が存在し、曇り度（cloud_percentage）が閾値未満なら快晴と判断
                    if (
                        closest_future_forecast is not None
                        and closest_future_forecast.cloud_percentage is not None
                        and closest_future_forecast.cloud_percentage
                        < app_preference.comfort_control.solar_cloud_threshold * 0.01
                    ):
                        SystemEventLogger.log_info(
                            "comfort_control_disabled.solar_cloud_threshold",
                            threshold=app_preference.comfort_control.solar_cloud_threshold,
                        )
                        # 快晴のため、PMV計算結果に基づいて最適なエアコン設定を決定する
                        aircon_settings = AirconSettingsDeterminer.determine_aircon_settings(
                            pmv_result, home_sensor, is_sleeping
                        )
        else:
            # 無効期間でなければ常にPMV計算に基づく最適なエアコン設定を適用する
            aircon_settings = AirconSettingsDeterminer.determine_aircon_settings(
                pmv_result, home_sensor, is_sleeping
            )

        if app_preference.database.enabled:
            # 前回のエアコン設定を取得し、経過時間をログに出力
            with DBSessionManager.auto_commit_session() as session:
                aircon_setting_service = AirconSettingService(session)
                current_aircon_settings, aircon_last_setting_time = (
                    aircon_setting_service.get_latest_aircon_settings()
                )
                if current_aircon_settings is None:
                    return AirconStateManager.update_aircon_settings(aircon_settings)
                if aircon_last_setting_time is not None:
                    hours, minutes = TimeHelper.calculate_elapsed_time(aircon_last_setting_time)
                    SystemEventLogger.log_elapsed_time(hours, minutes)

                # エアコンの設定が必要か確認し、更新
                if AirconOperation.update_aircon_if_necessary(
                    aircon_settings, current_aircon_settings, outdoor_temperature
                ):
                    aircon_change_intarval_service = AirconChangeIntarvalService(session)
                    aircon_change_intarval_service.update_start_time_if_exists(
                        aircon_settings.mode, outdoor_temperature
                    )
                return aircon_settings
        else:
            # データベースを使わない場合、エアコンの状態を直接更新
            return AirconStateManager.update_aircon_settings(aircon_settings)

    def update_circulator_settings(
        self,
        home_sensor: HomeSensor,
        circulator_settings_heat_conditions: CirculatorSettings,
        is_sleeping: bool,
        outdoor_temperature: float,
    ) -> CirculatorSettings:
        """
        サーキュレーターの状態を更新する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            circulator_settings_heat_conditions (CirculatorSettings): サーキュレーターの状態
            is_sleeping (bool): 寝ている時間
            outdoor_or_forecast_temperature (float): 室内または予報気温
        Returns:
            CirculatorSettings: サーキュレーターの状態
        """
        # 初期化
        circulator_settings = CirculatorSettings()

        if app_preference.circulator.enabled:
            # 前回のサーキュレーター設定を取得
            with DBSessionManager.session() as session:
                circulator_setting_service = CirculatorSettingService(session)
                current_circulator_settings = (
                    circulator_setting_service.get_latest_circulator_settings()
                )

            if is_sleeping:
                # 就寝中は風量を0に設定
                circulator_settings.power = Circulator.set_circulator(
                    current_circulator_settings, 0
                )
                circulator_settings.fan_speed = 0
            else:
                # 送風で節電する場合
                if circulator_settings_heat_conditions.power == PowerMode.ON:
                    # サーキュレーターは風量と電源を設定できないので、現在との差分を考慮して設定
                    circulator_settings.power = Circulator.set_circulator(
                        current_circulator_settings, circulator_settings_heat_conditions.fan_speed
                    )
                    circulator_settings.fan_speed = circulator_settings_heat_conditions.fan_speed
                else:
                    # 温度差に基づいてサーキュレーターを設定
                    if home_sensor.sub:
                        circulator_settings = Circulator.set_fan_speed_based_on_temperature_diff(
                            outdoor_temperature,
                            home_sensor.sub.air_quality.temperature
                            - home_sensor.main.air_quality.temperature,
                            current_circulator_settings,
                        )

            # ログ出力
            SystemEventLogger.log_circulator_settings(
                current_circulator_settings, circulator_settings
            )

        return circulator_settings

    def record_environment_data(
        self,
        home_sensor: HomeSensor,
        pmv: PMVResult,
        aircon_settings: AirconSettings,
        circulator_settings: CirculatorSettings,
    ) -> None:
        """
        環境データを記録する
        Args:
            measurement_time (datetime.datetime): 現在時刻
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv (PMVResults): PMV計算結果
            aircon_settings (AirconSettings): エアコンの設定
            circulator_settings (CirculatorSettings): サーキュレーターの設定
        """
        # データベースを使用する場合
        if app_preference.database.enabled:
            with DBSessionManager.session() as session:
                # エアコンの状態を記録
                aircon_intensity_score_service = AirconIntensityScoreService(session)
                scores = aircon_intensity_score_service.get_aircon_intensity_scores(
                    TimeHelper.get_current_time()
                )

                SystemEventLogger.log_aircon_scores(scores)

            with DBSessionManager.auto_commit_session() as session:
                measurement_service = MeasurementService(session)
                measurement_service.create_measurement_and_related_data(
                    measurement_time=TimeHelper.get_current_time(),
                    home_sensor=home_sensor,
                    pmv_result=pmv,
                    aircon_settings=aircon_settings,
                    circulator_settings=circulator_settings,
                )

                # 昨日のエアコン強度スコアを登録
                aircon_intensity_score_service = AirconIntensityScoreService(session)
                aircon_intensity_score_service.register_yesterday_intensity_score()

    def get_closest_future_forecast(self) -> WeatherForecastHourlyModel | None:
        """
        現在時刻を基準に次の時間単位の天気予報を取得する
        Returns:
            WeatherForecastHourlyModel: 天気予報データ
        """
        if app_preference.database.enabled:
            with DBSessionManager.session() as session:
                weather_service = WeatherForecastHourlyService(session)
                return weather_service.get_closest_future_forecast()
        return None

    def is_comfort_control_disabled(self) -> bool:
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
