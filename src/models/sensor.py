from typing import Optional
import common.constants as constants
from models.air_quality import AirQuality


class Sensor:
    """
    センサー情報を格納するためのクラス。

    Attributes:
        id (str): センサーのID（例: "floor"）
        label (str): センサーのラベル（例: "リビング"）
        location (str): センサーの設置場所（例: "床"）
        type (str): センサーの種類（例: "温湿度計"）
        air_quality (Optional[AirQuality]): センサーの空気質情報（省略可能）
    """

    def __init__(
        self,
        id: str,
        label: str,
        location: str,
        type: constants.SensorType,
        air_quality: Optional[AirQuality] = None,
    ):
        """
        初期化メソッド。

        Args:
            id (str): センサーのID
            label (str): センサーのラベル
            location (str): センサーの設置場所
            type (constants.SensorType): センサーの種類
            air_quality (Optional[AirQuality]): 空気質情報（省略可能）
        """
        self.id = id
        self.label = label
        self.location = location
        self.type = type
        self.air_quality = air_quality

    @property
    def id(self):
        """センサーIDのプロパティ"""
        return self._id

    @id.setter
    def id(self, value: str):
        """センサーIDのセッター"""
        if not isinstance(value, str):
            raise ValueError("IDは文字列である必要があります")
        self._id = value

    @property
    def label(self):
        """ラベルのプロパティ"""
        return self._label

    @label.setter
    def label(self, value: str):
        """ラベルのセッター"""
        if not isinstance(value, str):
            raise ValueError("ラベルは文字列である必要があります")
        self._label = value

    @property
    def location(self):
        """設置場所のプロパティ"""
        return self._location

    @location.setter
    def location(self, value: str):
        """設置場所のセッター"""
        if not isinstance(value, str):
            raise ValueError("設置場所は文字列である必要があります")
        self._location = value

    @property
    def type(self):
        """センサーの種類のプロパティ"""
        return self._type

    @type.setter
    def type(self, value: constants.SensorType):
        """センサーの種類のセッター"""
        if not isinstance(value, constants.SensorType):
            raise ValueError("無効なセンサーの種類です")
        self._type = value

    @property
    def air_quality(self):
        """空気質情報のプロパティ"""
        return self._air_quality

    @air_quality.setter
    def air_quality(self, value: Optional[AirQuality]):
        """空気質情報のセッター"""
        if value is not None and not isinstance(value, AirQuality):
            raise ValueError("空気質情報はAirQuality型でなければなりません")
        self._air_quality = value