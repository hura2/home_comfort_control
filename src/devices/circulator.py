import common.constants as constants
from api.smart_devices.smart_device_factory import SmartDeviceFactory
from models.circulator_state import CirculatorState
from settings.circulator_settings import CirculatorSettings
from settings.general_settings import GeneralSettings


class Circulator:
    """
    サーキュレーターを操作するためのクラス。

    このクラスは、サーキュレーターのファンスピードを調整したり、電源をオン・オフしたりするための
    メソッドを提供します。また、温度差に基づいてファンスピードを設定する機能も持っています。

    メソッド:
        - adjust_fan_speed: 現在のファンスピードをターゲットスピードに調整します。
        - set_circulator: サーキュレーターの電源とファンスピードを設定します。
        - set_fan_speed_based_on_temperature_diff: 温度差に基づいてファンスピードを設定します。
    """

    # @staticmethod
    # def adjust_fan_speed(current_speed: int, target_speed: int) -> int:
    #     """
    #     現在のファンスピードをターゲットスピードに調整します。

    #     Args:
    #         current_speed (int): 現在のファンスピード（0以上の整数）。
    #         target_speed (int): 調整したいターゲットスピード（0以上の整数）。

    #     Returns:
    #         int: 調整後のファンスピード。target_speedに達するまでループします。
    #     """
    #     while current_speed != target_speed:
    #         if target_speed > current_speed:
    #             SwitchBotApi.increase_circulator_volume()  # ファンスピードを増加させる
    #             current_speed += 1
    #         else:
    #             SwitchBotApi.decrease_circulator_volume()  # ファンスピードを減少させる
    #             current_speed -= 1
    #     return current_speed

    @staticmethod
    def set_circulator(
        current_circulator_state: CirculatorState, target_fan_speed: int
    ) -> constants.CirculatorPower:
        """
        サーキュレーターの電源とファンスピードを設定します。

        Args:
            current_circulator_state (CirculatorState): 現在のサーキュレーターの状態。
            target_fan_speed (int): 設定したいターゲットファンスピード（0以上の整数）。

        Returns:
            str: 更新後の電源状態（'ON'または'OFF'）。
        """
        smart_device = SmartDeviceFactory.create_device()
        power = current_circulator_state.power
        if target_fan_speed == 0:
            # ターゲットファンスピードが0の場合、サーキュレーターを停止する
            if power == constants.CirculatorPower.ON:
                smart_device.circulator_fan_speed(
                    target_fan_speed, current_circulator_state.fan_speed
                )
                smart_device.circulator_off()  # 電源をオフにする
                power = constants.CirculatorPower.OFF
        else:
            # ターゲットファンスピードが0でない場合、サーキュレーターをオンにする
            if power == constants.CirculatorPower.OFF:
                smart_device.circulator_on()  # 電源をオンにする
                power = constants.CirculatorPower.ON

            smart_device.circulator_fan_speed(
                target_fan_speed, current_circulator_state.fan_speed
            )

        return power

    @staticmethod
    def set_fan_speed_based_on_temperature_diff(
        outdoor_temperature: float,
        forest_max_temperature: float,
        temperature_diff: float,
        current_circulator_state: CirculatorState,
    ) -> CirculatorState:
        """
        温度差に基づいてファンスピードを設定します。

        Args:
            outdoor_temperature (float): 屋外の温度（摂氏）。
            forecast_max_temperature (float): 予報された最高気温（摂氏）。
            temperature_diff (float): 室内外の温度差（摂氏）。
            current_circulator_state (CirculatorState): 現在のサーキュレーターの状態。

        Returns:
            CirculatorState: 更新後の電源状態（'ON'または'OFF'）と設定したファンスピード。
        """
        # 設定を取得
        settings = GeneralSettings()
        circulator_settings = CirculatorSettings()

        # 高温時および高温以外のスピード設定を取得
        high_speed_thresholds = circulator_settings.high_speed_thresholds
        normal_speed_thresholds = circulator_settings.normal_speed_thresholds

        temperature = (
            outdoor_temperature if outdoor_temperature is not None else forecast_max_temperature
        )

        # 屋外の温度に応じてしきい値を選択
        threshold_speeds = (
            high_speed_thresholds
            if temperature >= settings.temperature_thresholds.high_temperature_threshold
            else normal_speed_thresholds
        )
        # 温度差に基づいてファンスピードを決定
        for item in threshold_speeds:  # 各辞書をイテレート
            threshold = item["threshold"]
            speed = item["speed"]
            if temperature_diff >= float(threshold):
                return CirculatorState(
                    Circulator.set_circulator(current_circulator_state, speed), speed
                )

        # 温度差がしきい値を満たさない場合はファンスピードを0に設定
        return CirculatorState(Circulator.set_circulator(current_circulator_state, 0), 0)

    @staticmethod
    def set_circulator_by_temperature(
        pmv: float, absolute_humidity: float, forecast_max_temperature: float
    ) -> CirculatorState:
        """
        気温に基づいてサーキュレーターの状態を設定します。

        Args:
            pmv (float): PMV値。
            absolute_humidity (float): 絶対湿度（g/m³）。
            forecast_max_temperature (float): 最高気温（天気予報から取得）。
            high_temp_threshold (float): 高温の判断基準温度。

        Returns:
            CirculatorState: サーキュレーターの状態。
        """
        settings = GeneralSettings()  # 設定を取得
        circulator_state = CirculatorState()  # サーキュレーターの状態を取得

        # 最高気温が設定した高温の判断基準温度を超えているか確認
        if forecast_max_temperature >= settings.temperature_thresholds.high_temperature_threshold:
            circulator_state.power = constants.CirculatorPower.ON  # サーキュレーターをオンにする
            # PMVがしきい値以上または絶対湿度が除湿しきい値以上の場合
            if (
                pmv >= settings.environment_settings.pmv_threshold
                or absolute_humidity >= settings.environment_settings.dehumidification_threshold
            ):
                circulator_state.fan_speed = 2  # サーキュレーターを稼働するスピードを設定
            else:
                circulator_state.fan_speed = 0  # サーキュレーターを停止する

        return circulator_state  # サーキュレーターの稼働状態とスピードを返す
