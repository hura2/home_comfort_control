from sqlalchemy.orm import Session

from models.sensor_reading_model import SensorReadingModel
from repository.queries.sensor_reading_queries import SensorReadingQueries
from repository.services.sensor_service import SensorService
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.sensor import Sensor


class SensorReadingService:
    """
    センサ測定値を管理するサービスクラス
    """

    def __init__(self, session: Session):
        """コンストラクタ"""
        # 各クエリクラスのインスタンスを初期化
        self.session = session
        self.sensor_reading_queries = SensorReadingQueries(session)

    def insert_home_sensor(self, measurement_id: int, home_sensor: HomeSensor):
        """
        ホームセンサーの測定値を挿入する

        Args:
            measurement_id (int): 測定ID
            home_sensor (HomeSensor): ホームセンサー
        """
        self.insert(measurement_id=measurement_id, sensor=home_sensor.main, category="main")
        self.insert(measurement_id=measurement_id, sensor=home_sensor.sub, category="sub")
        for supplementary in home_sensor.supplementaries:
            self.insert(
                measurement_id=measurement_id, sensor=supplementary, category="supplementary"
            )
        self.insert(measurement_id=measurement_id, sensor=home_sensor.outdoor, category="outdoor")

    def insert(
        self, measurement_id: int, sensor: Sensor | None, category: str
    ) -> SensorReadingModel | None:
        """
        センサーの測定値を挿入する

        Args:
            measurement_id (int): 測定ID
            sensor (Sensor): センサー
            category (str): センサーのカディゴリー

        Returns:
            SensorReadingModel: 挿入されたセンサーの測定値
        """
        if sensor is None:
            return None
        sensor_model = SensorService(self.session).insert_or_get(sensor=sensor, category=category)

        return self.sensor_reading_queries.insert(
            measurement_id=measurement_id,
            sensor_id=sensor_model.id,
            temperature=sensor.air_quality.temperature,
            humidity=sensor.air_quality.humidity,
            co2_level=sensor.air_quality.co2_level,
        )
