from api.smart_home_devices.smart_home_device_factory import SmartHomeDeviceFactory
from settings import electric_fan_preference
from shared.dataclass.electric_fan_settings import ElectricFanSettings
from shared.enums.power_mode import PowerMode


class ElectricFan:
    """
    扇風機を操作するためのクラス。

    このクラスは、扇風機のファンスピードを調整したり、電源をオン・オフしたりするためのメソッドを提供します。

    """

    @staticmethod
    def set_power(
        current_electric_fan_settings: ElectricFanSettings, power: PowerMode
    ) -> PowerMode:
        """
        扇風機の電源を設定します。

        Args:
            power (PowerMode): 電源状態（'ON'または'OFF'）。

        Returns:
            PowerMode: 更新後の電源状態（'ON'または'OFF'）。
        """
        smart_device = SmartHomeDeviceFactory.create_device()
        if power == PowerMode.ON:
            if current_electric_fan_settings.power == PowerMode.OFF:
                smart_device.electric_fan_on()  # 電源をオンにする
                return PowerMode.ON
        else:
            if current_electric_fan_settings.power == PowerMode.ON:
                smart_device.electric_fan_off()  # 電源をオフにする
                return PowerMode.OFF

        return current_electric_fan_settings.power

    @staticmethod
    def set_electric_fan_by_temperature(
        current_electric_fan_settings: ElectricFanSettings, mean_radiant_temperature: float
    ) -> ElectricFanSettings:
        """
        平均放射温度に基づいて扇風機の状態を設定します。

        Args:
            current_electric_fan_settings (ElectricFanSettings): 現在の扇風機の状態。
            mean_radiant_temperature (float): 温度（°C）。

        Returns:
            ElectricFanSettings: 扇風機の状態。
        """
        electric_fan_settings = ElectricFanSettings(
            power=current_electric_fan_settings.power,
            fan_speed=current_electric_fan_settings.fan_speed,
            swing=current_electric_fan_settings.swing,
            vertical_swing=current_electric_fan_settings.vertical_swing,
            rhythm=current_electric_fan_settings.rhythm,
        )  # 扇風機の現在状態を取得
        smart_device = SmartHomeDeviceFactory.create_device()
        # 平均放射温度が設定した閾値の判断基準温度を超えているか確認
        if (
            mean_radiant_temperature
            >= electric_fan_preference.fan_on_feels_like_temperature_threshold
        ):
            # 電源をオンにする
            electric_fan_settings.power = ElectricFan.set_power(current_electric_fan_settings, PowerMode.ON)
        else:
            # 電源をオフにする
            electric_fan_settings.power = ElectricFan.set_power(current_electric_fan_settings, PowerMode.OFF)

        return electric_fan_settings  # 扇風機の稼働状態を返す
