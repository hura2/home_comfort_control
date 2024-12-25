from sqlalchemy.orm import Session

from models.sensor_model import SensorModel
from repository.queries.sensor_queries import SensorQueries
from shared.dataclass.sensor import Sensor


class SensorService:
    """センサを管理するサービスクラス"""

    def __init__(self, session: Session):
        """コンストラクタ"""
        # 各クエリクラスのインスタンスを初期化
        self.session = session
        self.sensor_queries = SensorQueries(session)

    def insert(self, sensor: Sensor, category: str) -> SensorModel:
        """
        センサ情報を挿入する
        
        Args:
            sensor (Sensor): センサー情報
            category (str): センサーのカディゴリー

        Returns:
            SensorModel: 新しく挿入されたセンサ情報
        """
        return self.sensor_queries.insert(
            sensor_code=sensor.id,
            label=sensor.label,
            location=sensor.location,
            sensor_type=sensor.type,
            category=category,
        )

    def insert_or_get(self, sensor: Sensor, category: str) -> SensorModel:
        """
        センサ情報を挿入するか、既に存在する場合は取得する
        
        Args:
            sensor (Sensor): センサー情報
            category (str): センサーのカディゴリー

        Returns:
            SensorModel: センサ情報
        """
        sensor_model = self.sensor_queries.get_sensor_by_sensor_code(sensor.id)
        if sensor_model is None:
            return self.insert(sensor=sensor, category=category)
        return sensor_model
