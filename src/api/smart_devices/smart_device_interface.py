from abc import ABC, abstractmethod

from api.smart_devices.smart_device_response import SmartDeviceResponse
from models.air_quality import AirQuality
from models.aircon_state import AirconState
from models.sensor import Sensor


class SmartDeviceInterface(ABC):
    @abstractmethod
    def circulator_on(self) -> SmartDeviceResponse:
        """サーキュレーターをオンにする"""
        pass

    @abstractmethod
    def circulator_off(self) -> SmartDeviceResponse:
        """サーキュレーターをオフにする"""
        pass

    @abstractmethod
    def circulator_fan_speed(
        self, speed: int, current_spped: int = None
    ) -> SmartDeviceResponse:
        """サーキュレーターのファン速度を設定する"""
        pass

    @abstractmethod
    def aircon(self, aircon_state: AirconState) -> SmartDeviceResponse:
        pass

    @abstractmethod
    def get_air_quality_by_sensor(self, sensor: Sensor) -> AirQuality:
        pass
