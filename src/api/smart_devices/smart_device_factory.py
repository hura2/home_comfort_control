from api.smart_devices.smart_device_interface import SmartDeviceInterface
from api.smart_devices.switchbot_api import SwitchBotApi
from common import constants
from settings.general_settings import GeneralSettings


class SmartDeviceFactory:

    @staticmethod
    def create_device() -> SmartDeviceInterface:
        settings = GeneralSettings()
        if settings.smart_device_settings.device_type == constants.SmartDeviceType.SWITCH_BOT.value:
            return SwitchBotApi()
        else:
            raise ValueError(f"Unknown device type: {settings.smart_device_settings.device_type}")
