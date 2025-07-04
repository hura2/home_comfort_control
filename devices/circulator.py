from api.smart_home_devices.smart_home_device_factory import SmartHomeDeviceFactory
from settings import app_preference, circulator_preference
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.enums.power_mode import PowerMode


class Circulator:
    """
    サーキュレーターを操作するためのクラス。

    このクラスは、サーキュレーターのファンスピードを調整したり、電源をオン・オフしたりするための
    メソッドを提供します。また、温度差に基づいてファンスピードを設定する機能も持っています。

    """

    @staticmethod
    def set_circulator(
        current_circulator_settings: CirculatorSettings, target_fan_speed: int
    ) -> PowerMode:
        """
        サーキュレーターの電源とファンスピードを設定します。

        Args:
            current_circulator_settings (CirculatorSettings): 現在のサーキュレーターの状態。
            target_fan_speed (int): 設定したいターゲットファンスピード（0以上の整数）。

        Returns:
            PowerMode: 更新後の電源状態（'ON'または'OFF'）。
        """
        smart_device = SmartHomeDeviceFactory.create_device()
        power = current_circulator_settings.power
        if target_fan_speed == 0:
            # ターゲットファンスピードが0の場合、サーキュレーターを停止する
            if power == PowerMode.ON:
                smart_device.circulator_fan_speed(
                    target_fan_speed, current_circulator_settings.fan_speed
                )
                smart_device.circulator_off()  # 電源をオフにする
                power = PowerMode.OFF
        else:
            # ターゲットファンスピードが0でない場合、サーキュレーターをオンにする
            if power == PowerMode.OFF:
                smart_device.circulator_on()  # 電源をオンにする
                power = PowerMode.ON

            smart_device.circulator_fan_speed(
                target_fan_speed, current_circulator_settings.fan_speed
            )

        return power

    @staticmethod
    def set_fan_speed_based_on_temperature_diff(
        outdoor_temperature: float,
        temperature_diff: float,
        current_circulator_settings: CirculatorSettings,
    ) -> CirculatorSettings:
        """
        温度差に基づいてファンスピードを設定します。

        Args:
            outdoor_temperature (float): 屋外の温度（摂氏）。
            temperature_diff (float): 室内外の温度差（摂氏）。
            current_circulator_settings (CirculatorSettings): 現在のサーキュレーターの状態。

        Returns:
            CirculatorSettings: 更新後の電源状態（'ON'または'OFF'）と設定したファンスピード。
        """
        # 設定を取得
        # 高温時および高温以外のスピード設定を取得
        high_speed_thresholds = circulator_preference.thresholds.high_temperature
        normal_speed_thresholds = circulator_preference.thresholds.normal_temperature

        # 屋外の温度に応じてしきい値を選択
        threshold_speeds = (
            high_speed_thresholds
            if outdoor_temperature >= app_preference.temperature_thresholds.high
            else normal_speed_thresholds
        )
        # 温度差に基づいてファンスピードを決定
        for item in threshold_speeds:  # 各辞書をイテレート
            threshold = item.temperature_deff
            speed = item.speed
            if temperature_diff >= float(threshold):
                return CirculatorSettings(
                    power=Circulator.set_circulator(current_circulator_settings, speed),
                    fan_speed=speed,
                )

        # 温度差がしきい値を満たさない場合はファンスピードを0に設定
        return CirculatorSettings(
            power=Circulator.set_circulator(current_circulator_settings, 0), fan_speed=0
        )

    @staticmethod
    def set_circulator_by_temperature(
        pmv: float, absolute_humidity: float, outdoor_temperature: float
    ) -> CirculatorSettings:
        """
        気温に基づいてサーキュレーターの状態を設定します。

        Args:
            pmv (float): PMV値。
            absolute_humidity (float): 絶対湿度（g/m³）。
            outdoor_temperature (float): 外気温度（°C）。

        Returns:
            CirculatorSettings: サーキュレーターの状態。
        """
        circulator_settings = CirculatorSettings()  # サーキュレーターの状態を取得

        # 最高気温が設定した高温の判断基準温度を超えているか確認
        # if outdoor_temperature >= app_preference.temperature_thresholds.high:
            # circulator_settings.power = PowerMode.ON  # サーキュレーターをオンにする
            # PMVがしきい値以上または絶対湿度が除湿しきい値以上の場合
            # if (
            #     pmv >= app_preference.environment.pmv_threshold
            #     or absolute_humidity >= app_preference.environment.dehumidification_threshold
            # ):
            #     circulator_settings.fan_speed = 2  # サーキュレーターを稼働するスピードを設定
            # else:
            #     circulator_settings.fan_speed = 0  # サーキュレーターを停止する

        return circulator_settings  # サーキュレーターの稼働状態とスピードを返す
