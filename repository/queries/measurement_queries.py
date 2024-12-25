from sqlalchemy.orm import Session

from models.measurement_model import MeasurementModel


class MeasurementQueries:
    """
    測定日時を管理するクエリクラス。
    """
    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(self, measurement_time: str) -> MeasurementModel:
        """
        測定日時を挿入する。

        Args:
            measurement_time (str): 測定日時

        Returns:
            MeasurementModel: 新しく挿入された測定日時
        """
        new_measurement = MeasurementModel(measurement_time=measurement_time)
        self.session.add(new_measurement)
        self.session.flush()
        return new_measurement
