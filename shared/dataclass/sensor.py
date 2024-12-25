from pydantic import BaseModel, field_validator, model_validator, root_validator

from shared.dataclass.air_quality import AirQuality
from shared.enums.sensor_type import SensorType
from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class Sensor(BaseModel):
    """
    センサー情報を格納するためのクラス。

    Attributes:
        id (str): センサーのID（例: "floor"）
        label (str): センサーのラベル（例: "リビング"）
        location (str): センサーの設置場所（例: "床"）
        type (str): センサーの種類（例: "温湿度計"）
        air_quality (AirQuality): センサーの空気質情報（省略可能）
    """

    id: str
    """センサーのID（例: "floor"）"""
    label: str
    """センサーのラベル（例: "リビング"）"""
    location: str
    """センサーの設置場所（例: "床"）"""
    type: SensorType
    """センサーの種類（例: "温湿度計"）"""
    air_quality: AirQuality = AirQuality()
    """センサーの空気質情報"""

    @field_validator("type", mode="before")
    def convert_type_to_enum(cls, value, field):
        # 文字列からEnumに変換
        try:
            # すでに SensorType 型であれば変換しない
            if isinstance(value, SensorType):
                return value
            value = SensorType.get_by_label(value)
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=Sensor,
                type=value,
            )
        return value

    # def __init__(
    #     self,
    #     id: str,
    #     label: str,
    #     location: str,
    #     type: SensorType,
    #     air_quality: Optional[AirQuality] = None,
    # ):
    #     """
    #     初期化メソッド。

    #     Args:
    #         id (str): センサーのID
    #         label (str): センサーのラベル
    #         location (str): センサーの設置場所
    #         type (constants.SensorType): センサーの種類
    #         air_quality (Optional[AirQuality]): 空気質情報（省略可能）
    #     """
    #     self.id = id
    #     self.label = label
    #     self.location = location
    #     self.type = type
    #     self.air_quality = air_quality

    # @property
    # def id(self):
    #     """センサーIDのプロパティ"""
    #     return self._id

    # @id.setter
    # def id(self, value: str):
    #     """センサーIDのセッター"""
    #     self._id = value

    # @property
    # def label(self):
    #     """ラベルのプロパティ"""
    #     return self._label

    # @label.setter
    # def label(self, value: str):
    #     """ラベルのセッター"""
    #     self._label = value

    # @property
    # def location(self):
    #     """設置場所のプロパティ"""
    #     return self._location

    # @location.setter
    # def location(self, value: str):
    #     """設置場所のセッター"""
    #     self._location = value

    # @property
    # def type(self):
    #     """センサーの種類のプロパティ"""
    #     return self._type

    # @type.setter
    # def type(self, value: SensorType):
    #     """センサーの種類のセッター"""
    #     self._type = value

    # @property
    # def air_quality(self):
    #     """空気質情報のプロパティ"""
    #     return self._air_quality

    # @air_quality.setter
    # def air_quality(self, value: Optional[AirQuality]):
    #     """空気質情報のセッター"""
    #     self._air_quality = value
