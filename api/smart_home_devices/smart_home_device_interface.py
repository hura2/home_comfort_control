from abc import ABC, abstractmethod

from api.smart_home_devices.smart_home_device_response import SmartHomeDeviceResponse
from shared.dataclass.air_quality import AirQuality
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.sensor import Sensor


class SmartHomeDeviceInterface(ABC):
    """
    スマートホームデバイスのインターフェースクラス。

    このクラスは、サーキュレーターやエアコンなどのスマートホームデバイスに
    関する操作を定義するための抽象基底クラスです。各デバイスクラスはこの
    インターフェースを実装し、具体的な動作を提供する必要があります。
    """

    @abstractmethod
    def circulator_on(self) -> SmartHomeDeviceResponse:
        """
        サーキュレーターをオンにするメソッド。

        サーキュレーターをオンにするための処理を行い、その結果を
        SmartHomeDeviceResponseとして返す。

        Returns:
            SmartHomeDeviceResponse: サーキュレーターのオン操作結果。
        """
        pass

    @abstractmethod
    def circulator_off(self) -> SmartHomeDeviceResponse:
        """
        サーキュレーターをオフにするメソッド。

        サーキュレーターをオフにするための処理を行い、その結果を
        SmartHomeDeviceResponseとして返す。

        Returns:
            SmartHomeDeviceResponse: サーキュレーターのオフ操作結果。
        """
        pass

    @abstractmethod
    def circulator_fan_speed(
        self, speed: int, current_spped: int | None = None
    ) -> SmartHomeDeviceResponse:
        """
        サーキュレーターのファン速度を設定するメソッド。

        指定された速度でサーキュレーターのファンを設定し、その結果を
        SmartHomeDeviceResponseとして返す。

        Args:
            speed (int): 設定するファンの速度。
            current_spped (int | None): 現在のファン速度。デフォルトはNone。

        Returns:
            SmartHomeDeviceResponse: ファン速度設定結果。
        """
        pass

    @abstractmethod
    def aircon(self, aircon_settings: AirconSettings) -> SmartHomeDeviceResponse:
        """
        エアコンを設定するメソッド。

        エアコンの状態を指定して設定を行い、その結果をSmartHomeDeviceResponseとして返す。

        Args:
            aircon_settings (AirconSettings): エアコンの設定情報。

        Returns:
            SmartHomeDeviceResponse: エアコン設定結果。
        """
        pass

    @abstractmethod
    def get_air_quality_by_sensor(self, sensor: Sensor) -> AirQuality:
        """
        センサーを使って空気品質を取得するメソッド。

        指定されたセンサーから空気品質を取得し、その情報をAirQualityオブジェクトとして返す。

        Args:
            sensor (Sensor): 空気品質を測定するためのセンサー。

        Returns:
            AirQuality: 測定された空気品質のデータ。
        """
        pass
