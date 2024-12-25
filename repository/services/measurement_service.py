from datetime import datetime

from sqlalchemy.orm import Session

from models.measurement_model import MeasurementModel
from repository.queries.measurement_queries import MeasurementQueries
from repository.services.aircon_setting_service import AirconSettingService
from repository.services.circulator_setting_service import CirculatorSettingService
from repository.services.pmv_service import PmvService
from repository.services.sensor_reading_service import SensorReadingService
from settings import app_preference
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.pmv_result import PMVResult


class MeasurementService:
    """
    測定データのサービスクラス
    """

    def __init__(self, session: Session):
        """コンストラクタ"""
        # 各クエリクラスのインスタンスを初期化
        self.session = session
        self.measurement_queries = MeasurementQueries(session)
        self.aircon_setting_service = AirconSettingService(session)
        self.pmv_service = PmvService(session)
        self.sensor_reading_service = SensorReadingService(session)
        self.circulator_setting_service = CirculatorSettingService(session)

    def create_measurement_and_related_data(
        self,
        measurement_time: datetime,
        home_sensor: HomeSensor,
        pmv_result: PMVResult,
        aircon_settings: AirconSettings,
        circulator_settings: CirculatorSettings,
    ) -> MeasurementModel:
        """
        Measurement とその関連するすべてのデータ（AirconSetting, PmvCalculation, SensorReading, CirculatorSetting）を
        同時に挿入するサービスメソッド。

        :param measurement_type: 測定の種類 ('temperature', 'co2', 'pmv' など)
        :param temperature: エアコン設定温度
        :param mode: エアコンモード ('cooling', 'heating' など)
        :param fan_speed: エアコンのファン速度 ('low', 'medium', 'high' など)
        :param pmv_value: PMVの計算値
        :param sensor_type: センサーの種類 (例: 'temperature', 'co2')
        :param sensor_value: センサーの測定値
        :param circulator_mode: サーキュレーターのモード
        :return: 挿入された Measurement インスタンス
        """
        # Measurementを挿入
        measurement = self.measurement_queries.insert(measurement_time.isoformat())

        # 関連データの挿入
        self.aircon_setting_service.insert(
            measurement_id=measurement.id,
            aircon_settings=aircon_settings,
        )

        self.pmv_service.insert(measurement_id=measurement.id, pmv_result=pmv_result)

        self.sensor_reading_service.insert_home_sensor(
            measurement_id=measurement.id, home_sensor=home_sensor
        )

        if app_preference.circulator.use_circulator:
            self.circulator_setting_service.insert(
                measurement_id=measurement.id, circulator_settings=circulator_settings
            )

        # 最後にMeasurementインスタンスを返す
        return measurement
