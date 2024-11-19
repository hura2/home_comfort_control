import datetime

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from api.jma_forecast_api import JmaForecastApi
from api.switchbot_api import SwitchBotApi
from common import constants
from db.aircon_min_runtime_manager import AirconMinRuntimeManager
from db.analytics import Analytics
from devices.aircon.aircon_operation import AirconOperation
from devices.aircon.aircon_settings_determiner import AirconSettingsDeterminer
from devices.aircon.aircon_state_manager import AirconStateManager
from devices.circulator import Circulator
from models.circulator_state import CirculatorState
from models.comfort_factors import ComfortFactors
from models.home_sensor import HomeSensor
from models.pmv_results import PMVResults
from settings.general_settings import GeneralSettings
from util.logger import LoggerUtil, logger
from util.thermal_comfort import ThermalComfort
from util.time import TimeUtil


class HomeComfortControl:
    """家の快適環境を制御するクラス"""

    def __init__(self, settings: GeneralSettings):
        self.settings = settings

    def initialize_home_sensor(self) -> HomeSensor:
        """
        センサー情報を取得する
        Returns:
            HomeSensor: センサー情報
        """
        # センサー情報を取得
        home_sensor = HomeSensor(
            main=self.settings.sensors.main,
            sub=self.settings.sensors.sub,
            supplementaries=self.settings.sensors.supplementaries,
            outdoor=self.settings.sensors.outdoor,
        )
        # mainセンサーの空気質情報を取得
        home_sensor.main.air_quality = SwitchBotApi.get_air_quality_by_sensor(
            self.settings.sensors.main
        )
        # subセンサーの設定がある場合、subセンサーの空気質情報を取得
        if self.settings.sensors.sub:
            home_sensor.sub.air_quality = SwitchBotApi.get_air_quality_by_sensor(
                self.settings.sensors.sub
            )
        # supplementariesセンサーの設定がある場合、supplementariesセンサーの空気質情報を取得
        if self.settings.sensors.supplementaries:
            for supplementary in home_sensor.supplementaries:
                supplementary.air_quality = SwitchBotApi.get_air_quality_by_sensor(supplementary)
        # outdoorセンサーの設定がある場合、outdoorセンサーの空気質情報を取得
        if self.settings.sensors.outdoor:
            home_sensor.outdoor.air_quality = SwitchBotApi.get_air_quality_by_sensor(
                self.settings.sensors.outdoor
            )
        return home_sensor

    def fetch_forecast_max_temperature(self) -> int:
        """天気予報の最高気温を取得する
        Returns:
            int: 最高気温
        """
        forecast_max_temperature = None  # 初期値
        # データベースを使用する場合
        if self.settings.database_settings.use_database:
            # データベースに保存されている最高気温を取得
            forecast_max_temperature = Analytics.get_or_insert_max_temperature()
        else:
            # データベースを使用しない場合は、現在の最高気温を取得
            forecast_max_temperature = JmaForecastApi.get_max_temperature_by_date(
                TimeUtil.get_current_time().date().isoformat()
            )

        return forecast_max_temperature if forecast_max_temperature else 20

    def is_within_sleeping_period(self, now: datetime.datetime) -> bool:
        """現在の時刻が就寝時間内かどうかをチェックする
        Args:
            now (datetime.datetime): 現在時刻
        Returns:
            bool: 就寝時間内ならTrue、それ以外ならFalse
        """
        # 起床時間を取得
        awake_period_start = TimeUtil.timezone().localize(
            datetime.datetime.combine(
                now.date(), self.settings.time_settings.awake_period.start_time
            )
        )
        # 就寝時間を取得
        awake_period_end = TimeUtil.timezone().localize(
            datetime.datetime.combine(now.date(), self.settings.time_settings.awake_period.end_time)
        )
        # 就寝中かどうかを判断（起床時間内ならFalse、それ以外ならTrue）
        return awake_period_start > now or awake_period_end < now

    def activate_circulator_in_heat_conditions(
        self, home_sensor: HomeSensor, pmv: float, forecast_max_temperature: int
    ) -> CirculatorState:
        """
        熱中症の場合、サーキュレーターをオンにする
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv (float): PMV値
            forecast_max_temperature (int): 最高気温予報
        Returns:
            CirculatorState: サーキュレーターの状態
        """
        # サーキュレーター使用設定が有効かどうかを確認
        if self.settings.circulator_settings.use_circulator:
            # サーキュレーターの状態を設定
            circulator_state = Circulator.set_circulator_by_temperature(
                pmv, home_sensor.average_indoor_absolute_humidity, forecast_max_temperature
            )
        return circulator_state

    def recalculate_pmv_with_circulator(
        self,
        home_sensor: HomeSensor,
        forecast_max_temperature: int,
        circulator_state: CirculatorState,
        comfort_factors: ComfortFactors,
    ) -> PMVResults:
        """
        PMV値を再計算する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            forecast_max_temperature (int): 最高気温予報
            circulator_state (CirculatorState): サーキュレーターの状態
            comfort_factors (ComfortFactors): コンフォーマンス因子の値
        Returns:
            PMVResults: PMV計算結果
        """
        pmv = None
        # サーキュレーター使用設定が有効かどうかを確認
        if self.settings.circulator_settings.use_circulator:
            # サーキュレーターをオンにしている場合、風量を増やしてPMV値を再計算
            if circulator_state.power == constants.CirculatorPower.ON:
                pmv = ThermalComfort.calculate_pmv(
                    home_sensor, forecast_max_temperature, comfort_factors, wind_speed=0.3
                )

        return pmv

    def update_aircon_state(
        self,
        home_sensor: HomeSensor,
        pmv_result: PMVResults,
        forecast_max_temperature: int,
        is_sleeping: bool,
    ) -> None:
        """
        エアコンの状態を更新する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv_result (PMVResults): PMV計算結果
            forecast_max_temperature (int): 最高気温予報
            is_sleeping (bool): 寝ている時間
        """
        # PMVを元にエアコンの設定を判断
        aircon_state = AirconSettingsDeterminer.determine_aircon_settings(
            pmv_result, home_sensor, is_sleeping
        )

        if self.settings.database_settings.use_database:
            # 前回のエアコン設定を取得し、経過時間をログに出力
            current_aircon_state, aircon_last_setting_time = Analytics.get_latest_aircon_state()
            hours, minutes = TimeUtil.calculate_elapsed_time(aircon_last_setting_time)
            LoggerUtil.log_elapsed_time(hours, minutes)

            # エアコンの設定が必要か確認し、更新
            if AirconOperation.update_aircon_if_necessary(
                aircon_state, current_aircon_state, forecast_max_temperature
            ):
                AirconMinRuntimeManager.update_start_time_if_exists(
                    aircon_state.mode, forecast_max_temperature
                )
        else:
            # データベースを使わない場合、エアコンの状態を直接更新
            LoggerUtil.log_aircon_state(current_aircon_state)
            AirconStateManager.update_aircon_state(aircon_state)

    def update_circulator_state(
        self,
        home_sensor: HomeSensor,
        circulator_state_heat_conditions: CirculatorState,
        is_sleeping: bool,
        outdoor_or_forecast_temperature: float,
    ) -> CirculatorState:
        """
        サーキュレーターの状態を更新する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            circulator_state_heat_conditions (CirculatorState): サーキュレーターの状態
            is_sleeping (bool): 寝ている時間
            outdoor_or_forecast_temperature (float): 室内または予報気温
        Returns:
            CirculatorState: サーキュレーターの状態
        """
        # 初期化
        circulator_state = CirculatorState()

        if self.settings.circulator_settings.use_circulator:
            # 前回のサーキュレーター設定を取得
            current_circulator_state = Analytics.get_latest_circulator_state()

            if is_sleeping:
                # 就寝中は風量を0に設定
                circulator_state.power = Circulator.set_circulator(current_circulator_state, 0)
                circulator_state.fan_speed = 0
            else:
                # 送風で節電する場合
                if circulator_state_heat_conditions.power == constants.CirculatorPower.ON:
                    # サーキュレーターは風量と電源を設定できないので、現在との差分を考慮して設定
                    circulator_state.power = Circulator.set_circulator(
                        current_circulator_state, circulator_state_heat_conditions.fan_speed
                    )
                    circulator_state.fan_speed = circulator_state_heat_conditions.fan_speed
                else:
                    # 温度差に基づいてサーキュレーターを設定
                    if home_sensor.sub:
                        circulator_state = Circulator.set_fan_speed_based_on_temperature_diff(
                            outdoor_or_forecast_temperature,
                            home_sensor.sub.air_quality.temperature
                            - home_sensor.main.air_quality.temperature,
                            current_circulator_state,
                        )

            # ログ出力
            LoggerUtil.log_circulator_state(current_circulator_state, circulator_state.fan_speed)

        return circulator_state

    def record_environment_data(
        self,
        home_sensor: HomeSensor,
        pmv: PMVResults,
        circulator_state: CirculatorState,
        now: datetime.datetime,
    ) -> None:
        """
        環境データを記録する
        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            pmv (PMVResults): PMV計算結果
            circulator_state (CirculatorState): サーキュレーターの状態
            now (datetime.datetime): 現在時刻
        """
        # データベースを使用する場合
        if self.settings.database_settings.use_database:
            # エアコンの状態を記録
            LoggerUtil.log_aircon_scores(Analytics.get_aircon_intensity_scores(now))

            # データを記録
            Analytics.insert_temperature_humidity(home_sensor)
            Analytics.insert_co2_sensor_data(home_sensor)
            Analytics.insert_surface_temperature(pmv.wall, pmv.ceiling, pmv.floor)
            Analytics.insert_pmv(pmv.pmv, pmv.met, pmv.clo, pmv.air)

            # サーキュレーターを使用する場合
            if self.settings.circulator_settings.use_circulator:
                Analytics.insert_circulator_state(circulator_state)

            # 昨日のエアコン強度スコアを登録
            Analytics.register_yesterday_intensity_score()

    def get_running_mean_temperature(self) -> None:
        # 例としてlocation_idが3のデータを取得
        result = Analytics.get_hourly_average_temperature(location_id=3)

        temp_array = [entry["average_temperature"] for entry in result]
        logger.info(temp_array)
        # 時間データの作成
        hours = np.array(range(len(temp_array))).reshape(-1, 1)

        # 2次の多項式特徴量を生成
        poly = PolynomialFeatures(degree=3)
        hours_poly = poly.fit_transform(hours)

        # 線形回帰モデルの作成と学習
        model = LinearRegression()
        model.fit(hours_poly, temp_array)

        # 1時間後の気温予測
        next_hour_poly = poly.transform([[len(temp_array)]])
        predicted_temperature = model.predict(next_hour_poly)

        logger.info(f"1時間後の予測気温: {predicted_temperature[0]:.2f}°C")
