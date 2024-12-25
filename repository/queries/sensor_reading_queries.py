from sqlalchemy.orm import Session

from models.sensor_reading_model import SensorReadingModel


class SensorReadingQueries:
    """
    センサ測定値を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(
        self,
        measurement_id: int,
        sensor_id: int,
        temperature: float,
        humidity: float,
        co2_level: float | None = None,
    ) -> SensorReadingModel:
        """
        センサ測定値を挿入する。

        Args:
            measurement_id (int): 測定値のID
            sensor_id (int): センサーのID
            temperature (float): 温度
            humidity (float): 湿度
            co2_level (float | None): CO2レベル

        Returns:
            SensorReadingModel: 新しく挿入されたセンサ測定値
        """

        new_sensor_reading = SensorReadingModel(
            measurement_id=measurement_id,
            sensor_id=sensor_id,
            temperature=temperature,
            humidity=humidity,
            co2_level=co2_level,
        )
        self.session.add(new_sensor_reading)
        self.session.flush()
        return new_sensor_reading
