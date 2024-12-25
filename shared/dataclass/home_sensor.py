from pydantic import BaseModel

from shared.dataclass.air_quality import AirQuality
from shared.dataclass.sensor import Sensor
from shared.enums.sensor_type import SensorType
from util.humidity_metrics import HumidityMetrics


class HomeSensor(BaseModel):
    """
    家のセンサー情報を表すクラス。

    Attributes:
        main (Sensor): メインのセンサー。必須項目。
        sub (Sensor | None): 追加の部屋のセンサー。オプション。
        supplementaries (List[Sensor]): 追加の部屋のセンサーリスト。デフォルトは空リスト。
        outdoor (Sensor | None): 屋外のセンサー。オプション。
    """

    main: Sensor
    """メインのセンサー。必須項目。"""
    sub: Sensor | None = None
    """追加の部屋のセンサー。オプション。"""
    supplementaries: list[Sensor] = []
    """追加の部屋のセンサーリスト。デフォルトは空リスト。"""
    outdoor: Sensor | None = None
    """屋外のセンサー。オプション。"""

    def add_air_quality_to_sensor(self, sensor: Sensor, air_quality: AirQuality) -> Sensor:
        """
        センサー情報と空気の質情報を結合する。

        Args:
            sensor (Sensor): センサーの情報
            air_quality (AirQuality): センサーから取得した空気の質情報

        Returns:
            Sensor: センサー情報と空気の質情報を結合したSensorオブジェクト
        """
        return Sensor(
            id=sensor.id,
            label=sensor.label,
            location=sensor.location,
            type=sensor.type,
            air_quality=air_quality,
        )

    @property
    def average_indoor_temperature(self) -> float:
        """室内の気温の平均を取得する"""
        indoor_temperatures = [self.main.air_quality.temperature]
        if self.sub:
            indoor_temperatures.append(self.sub.air_quality.temperature)
        indoor_temperatures.extend(
            [supplementary.air_quality.temperature for supplementary in self.supplementaries]
        )
        return sum(indoor_temperatures) / len(indoor_temperatures)

    @property
    def average_indoor_humidity(self) -> float:
        """室内の湿度の平均を取得する"""
        indoor_humidities = [self.main.air_quality.humidity]
        if self.sub:
            indoor_humidities.append(self.sub.air_quality.humidity)
        indoor_humidities.extend(
            [supplementary.air_quality.humidity for supplementary in self.supplementaries]
        )
        return sum(indoor_humidities) / len(indoor_humidities)

    @property
    def average_indoor_absolute_humidity(self) -> float:
        """室内の絶対湿度の平均を取得する"""
        indoor_absolute_humidities = [self.main.air_quality.absolute_humidity]
        if self.sub:
            indoor_absolute_humidities.append(self.sub.air_quality.absolute_humidity)
        indoor_absolute_humidities.extend(
            [supplementary.air_quality.absolute_humidity for supplementary in self.supplementaries]
        )
        return sum(indoor_absolute_humidities) / len(indoor_absolute_humidities)

    @property
    def indoor_dew_point(self) -> float:
        """室内の露点を取得する"""
        return HumidityMetrics.calculate_dew_point(
            self.average_indoor_temperature, self.average_indoor_humidity
        )

    @property
    def outdoor_absolute_humidity(self) -> float:
        """屋外の絶対湿度を取得する"""
        return self.outdoor.air_quality.absolute_humidity if self.outdoor else float("-inf")

    @property
    def outdoor_dew_point(self) -> float | None:
        """屋外の露点を取得する"""
        if self.outdoor:
            return HumidityMetrics.calculate_dew_point(
                self.outdoor.air_quality.temperature, self.outdoor_absolute_humidity
            )
        return None

    @property
    def main_co2_level(self) -> int | None:
        """CO2レベルを取得する"""
        if self.main.type == SensorType.CO2:
            return self.main.air_quality.co2_level
        elif self.sub and self.sub.type == SensorType.CO2:
            return self.sub.air_quality.co2_level
        else:
            for supplementary in self.supplementaries:
                if supplementary.type == SensorType.CO2:
                    return supplementary.air_quality.co2_level
            return None

    @property
    def average_indoor_sensor(self) -> Sensor:
        """室内の平均センサー情報を取得する"""
        return Sensor(
            id="",
            label="室内平均",
            location="平均",
            type=SensorType.TEMPERATURE_HUMIDITY,
            air_quality=AirQuality(
                temperature=self.average_indoor_temperature,
                humidity=self.average_indoor_humidity,
            ),
        )


# Pydanticのモデルを使用することで、センサー情報が適切に検証されます

# from typing import List, Optional

# from shared.dataclass.air_quality import AirQuality
# from shared.dataclass.sensor import Sensor
# from shared.enums.sensor_type import SensorType
# from util.humidity_metrics import HumidityMetrics


# class HomeSensor:
#     """
#     家のセンサー情報を表すクラス。

#     Attributes:
#         main (Sensor): メインのセンサー。必須項目。
#         sub (Optional[Sensor]): 追加の部屋のセンサー。オプション。
#         supplementaries (List[Sensor]): 追加の部屋のセンサーリスト。デフォルトは空リスト。
#         outdoor (Optional[Sensor]): 屋外のセンサー。オプション。
#     """

#     def __init__(
#         self,
#         main: Sensor,
#         sub: Optional[Sensor] = None,
#         supplementaries: Optional[List[Sensor]] = None,
#         outdoor: Optional[Sensor] = None,
#     ):
#         """
#         初期化メソッド。各センサー情報を受け取る。

#         Args:
#             main (Sensor): メインのセンサー。
#             sub (Optional[Sensor]): 追加の部屋のセンサー（省略可能）。
#             supplementaries (List[Sensor]): 追加の部屋のセンサーリスト（省略可能）。
#             outdoor (Optional[Sensor]): 屋外のセンサー（省略可能）。
#         """
#         # main センサーは必須なので、Noneチェックを行う
#         if not isinstance(main, Sensor):
#             raise ValueError("main センサーは Sensor 型である必要があります")

#         self.main = main  # セッターを使ってセット
#         self.sub = sub  # セッターを使ってセット
#         self.supplementaries = supplementaries if supplementaries else []
#         self.outdoor = outdoor  # セッターを使ってセット

#     # main のゲッターとセッター
#     @property
#     def main(self) -> Sensor:
#         """メインセンサーの取得"""
#         return self._main

#     @main.setter
#     def main(self, sensor: Sensor) -> None:
#         """メインセンサーの設定"""
#         if not isinstance(sensor, Sensor):
#             raise ValueError("main センサーは Sensor 型である必要があります")
#         self._main = sensor

#     # sub のゲッターとセッター
#     @property
#     def sub(self) -> Optional[Sensor]:
#         """追加の部屋のセンサーの取得"""
#         return self._sub

#     @sub.setter
#     def sub(self, sensor: Optional[Sensor]) -> None:
#         """追加の部屋のセンサーの設定"""
#         if sensor is not None and not isinstance(sensor, Sensor):
#             raise ValueError("sub センサーは Sensor 型である必要があります")
#         self._sub = sensor

#     # supplementaries のゲッターとセッター
#     @property
#     def supplementaries(self) -> List[Sensor]:
#         """追加の部屋のセンサーリストの取得"""
#         return self._supplementaries

#     @supplementaries.setter
#     def supplementaries(self, sensors: List[Sensor]) -> None:
#         """追加の部屋のセンサーリストの設定"""
#         if not all(isinstance(sensor, Sensor) for sensor in sensors):
#             raise ValueError("supplementaries は Sensor 型のリストである必要があります")
#         self._supplementaries = sensors

#     # outdoor のゲッターとセッター
#     @property
#     def outdoor(self) -> Optional[Sensor]:
#         """屋外センサーの取得"""
#         return self._outdoor

#     @outdoor.setter
#     def outdoor(self, sensor: Optional[Sensor]) -> None:
#         """屋外センサーの設定"""
#         if sensor is not None and not isinstance(sensor, Sensor):
#             raise ValueError("outdoor センサーは Sensor 型である必要があります")
#         self._outdoor = sensor

#     @staticmethod
#     def add_air_quality_to_sensor(sensor: Sensor, air_quality: AirQuality) -> Sensor:
#         """
#         センサー情報と空気の質情報を結合する。

#         Args:
#             sensor (Sensor): センサーの情報
#             air_quality (AirQuality): センサーから取得した空気の質情報

#         Returns:
#             Sensor: センサー情報と空気の質情報を結合したSensorオブジェクト
#         """
#         return Sensor(
#             id=sensor.id,
#             label=sensor.label,
#             location=sensor.location,
#             type=sensor.type,
#             air_quality=air_quality,
#         )

#     @property
#     def average_indoor_temperature(self) -> float:
#         """室内の気温の平均を取得する"""
#         indoor_temperatures = [self.main.air_quality.temperature]
#         if self.sub:
#             indoor_temperatures.append(self.sub.air_quality.temperature)
#         indoor_temperatures.extend(
#             [supplementary.air_quality.temperature for supplementary in self.supplementaries]
#         )

#         return sum(indoor_temperatures) / len(indoor_temperatures)

#     @property
#     def average_indoor_humidity(self) -> float:
#         """室内の湿度の平均を取得する"""
#         indoor_humidities = [self.main.air_quality.humidity]
#         if self.sub:
#             indoor_humidities.append(self.sub.air_quality.humidity)
#         indoor_humidities.extend(
#             [supplementary.air_quality.humidity for supplementary in self.supplementaries]
#         )

#         return sum(indoor_humidities) / len(indoor_humidities)

#     @property
#     def average_indoor_absolute_humidity(self) -> float:
#         """室内の絶対湿度の平均を取得する"""
#         indoor_absolute_humidities = [self.main.air_quality.absolute_humidity]
#         if self.sub:
#             indoor_absolute_humidities.append(self.sub.air_quality.absolute_humidity)
#         indoor_absolute_humidities.extend(
#             [supplementary.air_quality.absolute_humidity for supplementary in self.supplementaries]
#         )

#         return sum(indoor_absolute_humidities) / len(indoor_absolute_humidities)

#     @property
#     def indoor_dew_point(self) -> float:
#         """室内の露点を取得する"""
#         return HumidityMetrics.calculate_dew_point(
#             self.average_indoor_temperature, self.average_indoor_humidity
#         )

#     @property
#     def outdoor_absolute_humidity(self) -> float:
#         """屋外の絶対湿度を取得する"""
#         return self.outdoor.air_quality.absolute_humidity if self.outdoor else None

#     @property
#     def outdoor_dew_point(self) -> float:
#         """屋外の露点を取得する"""
#         return HumidityMetrics.calculate_dew_point(
#             self.outdoor.air_quality.temperature, self.outdoor_absolute_humidity
#         )

#     @property
#     def main_co2_level(self) -> int:
#         if self.main.type == SensorType.CO2:
#             return self.main.air_quality.co2_level
#         elif self.sub and self.sub.type == SensorType.CO2:
#             return self.sub.air_quality.co2_level
#         else:
#             for supplementary in self.supplementaries:
#                 if supplementary.type == SensorType.CO2:
#                     return supplementary.air_quality.co2_level
#             return None

#     @property
#     def average_indoor_sensor(self) -> Sensor:
#         return Sensor(
#             id="",
#             label="室内平均",
#             location="平均",
#             type=SensorType.TEMPERATURE_HUMIDITY,
#             air_quality=AirQuality(
#                 temperature=self.average_indoor_temperature,
#                 humidity=self.average_indoor_humidity,
#             ),
#         )
