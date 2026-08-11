from datetime import datetime

from sqlalchemy.orm import Session

from models.measurement_model import MeasurementModel
from repository.queries.measurement_queries import MeasurementQueries
from repository.services.aircon_setting_service import AirconSettingService
from repository.services.circulator_setting_service import CirculatorSettingService
from repository.services.electric_fan_setting_service import ElectricFanSettingService
from repository.services.pmv_service import PmvService
from repository.services.sensor_reading_service import SensorReadingService
from settings import app_preference
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.dataclass.electric_fan_settings import ElectricFanSettings
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
        self.electric_fan_setting_service = ElectricFanSettingService(session)

    def create_measurement_and_related_data(
        self,
        measurement_time: datetime,
        home_sensor: HomeSensor,
        pmv_result: PMVResult,
        aircon_settings: AirconSettings,
        circulator_settings: CirculatorSettings,
        electric_fan_settings: ElectricFanSettings
    ) -> MeasurementModel:
        """
        Measurement とその関連するすべてのデータ（AirconSetting, PmvCalculation, SensorReading, CirculatorSetting）を
        同時に挿入するサービスメソッド。

        Args:
            measurement_time (datetime): 測定時刻
            home_sensor (HomeSensor): ホームセンサーの温度情報
            pmv_result (PMVResult): PMV計算結果
            aircon_settings (AirconSettings): 空調設定
            circulator_settings (CirculatorSettings): 冷却機設定
            electric_fan_settings (ElectricFanSettings): 扇風機設定

        Returns:
            MeasurementModel: 新しく挿入された測定日時
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

        if app_preference.circulator.enabled:
            self.circulator_setting_service.insert(
                measurement_id=measurement.id, circulator_settings=circulator_settings
            )

        if app_preference.electric_fan.enabled:
            self.electric_fan_setting_service.insert(
                measurement_id=measurement.id, electric_fan_settings=electric_fan_settings
            )

        # 最後にMeasurementインスタンスを返す
        return measurement
