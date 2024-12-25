from api.smart_home_devices.smart_home_device_interface import SmartHomeDeviceInterface
from api.smart_home_devices.switchbot_api import SwitchBotApi
from settings import app_preference
from shared.enums.smart_home_device import SmartHomeDevice


class SmartHomeDeviceFactory:
    """
    スマートホームデバイスを生成するファクトリークラス
    """

    @classmethod
    def create_device(cls) -> SmartHomeDeviceInterface:
        """
        スマートホームデバイスを生成するファクトリーメソッド。

        設定ファイルからデバイスの種類を取得し、その種類に基づいて
        対応するデバイスインスタンスを生成して返す。
        現在はSwitchBotデバイスのみサポートしており、それ以外のデバイスタイプは
        TranslatedValueErrorをスローする。

        Returns:
            SmartHomeDeviceInterface: 生成されたスマートホームデバイスのインスタンス。

        Raises:
            TranslatedValueError: 設定ファイルで指定されたデバイスタイプがサポートされていない場合。
        """
        if app_preference.smart_home_device.device_type == SmartHomeDevice.SWITCH_BOT:
            return SwitchBotApi()  # SwitchBotデバイスを生成して返す

        return SwitchBotApi()
