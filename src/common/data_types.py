import dataclasses
from typing import List, Optional

# 定数を管理するファイル
import common.constants as constants


@dataclasses.dataclass
class PMVResults:
    """
    PMV（Predicted Mean Vote）計算結果を表すデータクラス。

    Attributes:
        pmv (float): PMV値（快適度指数）。
        ppd (float): PPD値（不快指数）。
        clo (float): 衣服の断熱性。
        air (float): 空気の速度。
        met (float): MET値（代謝当量）。
        wall (float): 壁表面温度。
        ceiling (float): 天井表面温度。
        floor (float): 床表面温度。
        mean_radiant_temperature (float): 平均放射温度。
        dry_bulb_temperature (float): 乾球温度。
        relative_air_speed (float): 相対風速。
        dynamic_clothing_insulation (float): 動的な衣服の断熱性。
    """

    pmv: float
    ppd: float
    clo: float
    air: float
    met: float
    wall: float
    ceiling: float
    floor: float
    mean_radiant_temperature: float
    dry_bulb_temperature: float
    relative_air_speed: float
    dynamic_clothing_insulation: float


@dataclasses.dataclass
class ComfortFactors:
    """
    MET（代謝当量）およびICL（快適さ指標）を保持するクラス。

    属性:
        met (float): MET値。通常は1.0〜2.0程度（活動レベルに応じて異なる）
        icl (float): ICL値。通常は0.0〜1.5程度（衣服の断熱性に基づく）
    """

    met: float  # 代謝当量（Metabolic Equivalent of Task）
    icl: float  # 衣服の断熱性（Intrinsic Clothing Insulation Level）

    def __post_init__(self):
        # MET値の範囲をチェック
        if not (0.8 <= self.met <= 3.0):
            raise ValueError(f"MET値は0.8〜3.0の範囲である必要があります。指定された値: {self.met}")

        # ICL値の範囲をチェック
        if not (0.0 <= self.icl <= 2.0):
            raise ValueError(f"ICL値は0.0〜2.0の範囲である必要があります。指定された値: {self.icl}")


@dataclasses.dataclass
class CirculatorState:
    """
    サーキュレーター
    """

    power: constants.CirculatorPower = constants.CirculatorPower.OFF
    fan_speed: int = 0


@dataclasses.dataclass
class AirconState:
    """
    エアコンの設定を表すデータクラス。

    Attributes:
        temperature (str): 温度設定。
        mode (constants.AirconMode): 動作モード設定（エアコンモード）。
        fan_speed (constants.AirconFanSpeed): 風速設定。
        power (constants.AirconPower): 電源設定。
        force_fan_below_dew_point (Optional[bool]): 露点温度を下回った場合に強制的に送風にするかどうかの設定。
    """

    temperature: str = "20"
    mode: constants.AirconMode = constants.AirconMode.FAN
    fan_speed: constants.AirconFanSpeed = constants.AirconFanSpeed.AUTO
    power: constants.AirconPower = constants.AirconPower.ON
    force_fan_below_dew_point: Optional[bool] = False  # デフォルトはFalse

    def __eq__(self, other):
        """
        他のAirconSettingオブジェクトと比較して、等しいかどうかを判定するメソッド。

        Args:
            other: 比較対象のオブジェクト。

        Returns:
            bool: オブジェクトが等しい場合はTrue、そうでない場合はFalse。
        """
        if isinstance(other, AirconState):
            return (
                self.temperature == other.temperature
                and self.mode == other.mode
                and self.fan_speed == other.fan_speed
                and self.power == other.power
            )
        return False

    def update_if_none(self, other):
        """
        別のAirconStateインスタンスの属性を基に、このインスタンスを更新します。
        Noneでない属性のみを更新します。

        Args:
            other (AirconState): 更新の基になるAirconStateオブジェクト。
        """
        if not isinstance(other, AirconState):
            raise TypeError("更新対象はAirconState型である必要があります。")

        for field in dataclasses.fields(self):
            attr_name = field.name
            other_value = getattr(other, attr_name)
            if other_value is not None:
                setattr(self, attr_name, other_value)


@dataclasses.dataclass
class PMVThresholdState:
    """PMVに基づくエアコンの設定を保持するデータクラス"""

    threshold: float  # PMV閾値
    aircon_state: AirconState  # エアコンの設定


@dataclasses.dataclass
class AirQuality:
    """
    空気の質を表すデータクラス。

    Attributes:
        temperature (float): 温度値。
        humidity (float): 湿度値。
        co2_level (float): CO2濃度。
    """

    temperature: float
    humidity: float
    co2_level: Optional[int] = None  # デフォルトはNone

    @property
    def absolute_humidity(self) -> float:
        """
        絶対湿度を計算するプロパティ。

        Returns:
            float: 絶対湿度 (g/m³)。
        """
        from util.thermal_comfort_calculator import ThermalComfortCalculator

        return ThermalComfortCalculator.calculate_absolute_humidity(self.temperature, self.humidity)


@dataclasses.dataclass
class Sensor:
    """
    センサー情報を格納するためのデータクラス。

    Attributes:
        id (str): センサーのID（例: "floor"）
        label (str): センサーのラベル（例: "リビング"）
        location (str): センサーの設置場所（例: "床"）
        type (str): センサーの種類（例: "温湿度計"）
    """

    id: str
    label: str
    location: str
    type: constants.SensorType
    air_quality: Optional[AirQuality] = None  # デフォルト値を設定


@dataclasses.dataclass
class HomeSensor:
    """
    家のセンサー情報を表すデータクラス。

    Attributes:
        main_room (AirQuality): メインの部屋の空気の質情報。
        rooms (List[AirQuality]): 追加の部屋の空気の質情報リスト。
        outdoor (Optional[AirQuality]): 屋外の空気の質情報。
    """

    main: Sensor
    sub: Optional[Sensor]
    supplementaries: List[Sensor] = dataclasses.field(default_factory=list)  # 追加の部屋の空気の質情報リスト
    outdoor: Optional[Sensor] = None  # 屋外の空気の質情報

    @staticmethod
    def add_air_quality_to_sensor(sensor: Sensor, air_quality: AirQuality) -> Sensor:
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
        indoor_temperatures.extend([supplementary.air_quality.temperature for supplementary in self.supplementaries])

        return sum(indoor_temperatures) / len(indoor_temperatures)

    @property
    def average_indoor_humidity(self) -> float:
        """室内の湿度の平均を取得する"""
        indoor_humidities = [self.main.air_quality.humidity]
        if self.sub:
            indoor_humidities.append(self.sub.air_quality.humidity)
        indoor_humidities.extend([supplementary.air_quality.humidity for supplementary in self.supplementaries])

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
        from util.thermal_comfort_calculator import ThermalComfortCalculator

        return ThermalComfortCalculator.calculate_dew_point(
            self.average_indoor_temperature, self.average_indoor_humidity
        )

    @property
    def outdoor_absolute_humidity(self) -> float:
        """屋外の絶対湿度を取得する"""
        return self.outdoor.air_quality.absolute_humidity if self.outdoor else None

    @property
    def outdoor_dew_point(self) -> float:
        """屋外の露点を取得する"""
        from util.thermal_comfort_calculator import ThermalComfortCalculator

        return ThermalComfortCalculator.calculate_dew_point(
            self.outdoor.air_quality.temperature, self.outdoor_absolute_humidity
        )

    @property
    def main_co2_level(self) -> int:
        if self.main.type == constants.SensorType.CO2:
            return self.main.air_quality.co2_level
        elif self.sub and self.sub.type == constants.SensorType.CO2:
            return self.sub.air_quality.co2_level
        else:
            for supplementary in self.supplementaries:
                if supplementary.type == constants.SensorType.CO2:
                    return supplementary.air_quality.co2_level
            return None

    @property
    def average_indoor_sensor(self) -> Sensor:
        return Sensor(
            id="",
            label="室内平均",
            location="平均",
            type=constants.SensorType.TEMPERATURE_HUMIDITY,
            air_quality=AirQuality(
                temperature=self.average_indoor_temperature,
                humidity=self.average_indoor_humidity,
            ),
        )
