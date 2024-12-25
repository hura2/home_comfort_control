from sqlalchemy.orm import Session

from models.sensor_model import SensorModel
from repository.queries.sensor_type_queries import SensorTypeQueries
from shared.enums.sensor_type import SensorType
from translations.translated_value_error import TranslatedValueError


class SensorQueries:
    """
    センサ情報を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(
        self, sensor_code: str, label: str, location: str, sensor_type: SensorType, category: str
    ) -> SensorModel:
        """
        センサ情報を挿入する。

        Args:
            sensor_code (str): センサコード
            label (str): センサラベル
            location (str): センサ設置場所
            sensor_type (SensorType): センサタイプ
            category (str): センサカディ

        Returns:
            SensorModel: 新しく挿入されたセンサ情報
        """
        # センサタイプの検証
        sensor_type_model = SensorTypeQueries(self.session).get_type_by_name(sensor_type.name)
        if sensor_type_model is None:
            raise TranslatedValueError(sensor_type=sensor_type.name)

        sensor_model = SensorModel(
            sensor_code=sensor_code,
            label=label,
            location=location,
            sensor_type_id=sensor_type_model.id,
            category=category,
        )
        self.session.add(sensor_model)
        self.session.flush()
        return sensor_model

    def get_sensor_by_sensor_code(self, sensor_code: str) -> SensorModel | None:
        """
        センサ情報を取得する。

        Args:
            sensor_code (str): センサコード

        Returns:
            SensorModel: センサ情報
        """
        return self.session.query(SensorModel).filter_by(sensor_code=sensor_code).first()
