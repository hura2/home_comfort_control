from typing import Optional

from common import constants


class AirconState:
    """
    エアコンの設定を表すクラス。

    Attributes:
        temperature (str): 温度設定。
        mode (constants.AirconMode): 動作モード設定（エアコンモード）。
        fan_speed (constants.AirconFanSpeed): 風速設定。
        power (constants.AirconPower): 電源設定。
        force_fan_below_dew_point (Optional[bool]): 露点温度を下回った場合に強制的に送風にするかどうかの設定。
    """

    def __init__(
        self,
        temperature: str = "20",
        mode: constants.AirconMode = constants.AirconMode.FAN,
        fan_speed: constants.AirconFanSpeed = constants.AirconFanSpeed.AUTO,
        power: constants.AirconPower = constants.AirconPower.ON,
        force_fan_below_dew_point: Optional[bool] = False,
    ):
        self.temperature = temperature
        self.mode = mode
        self.fan_speed = fan_speed
        self.power = power
        self.force_fan_below_dew_point = force_fan_below_dew_point

    def __eq__(self, other):
        """
        他のAirconStateオブジェクトと比較して、等しいかどうかを判定するメソッド。

        Args:
            other: 比較対象のオブジェクト。

        Returns:
            bool: オブジェクトが等しい場合はTrue、そうでない場合はFalse。
        """
        if isinstance(other, AirconState):
            return (
                self._temperature == other._temperature
                and self._mode == other._mode
                and self._fan_speed == other._fan_speed
                and self._power == other._power
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

        for attr_name in vars(self):  # dataclasses.fieldsは不要
            other_value = getattr(other, attr_name)
            if other_value is not None:
                setattr(self, attr_name, other_value)

    @property
    def temperature(self):
        """温度設定のプロパティ"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: str):
        """温度設定のセッター"""
        if not value.isdigit():
            raise ValueError("温度は数値でなければなりません")
        self._temperature = value

    @property
    def mode(self):
        """動作モード設定のプロパティ"""
        return self._mode

    @mode.setter
    def mode(self, value: constants.AirconMode):
        """動作モード設定のセッター"""
        if not isinstance(value, constants.AirconMode):
            raise ValueError("無効なエアコンモードです")
        self._mode = value

    @property
    def fan_speed(self):
        """風速設定のプロパティ"""
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, value: constants.AirconFanSpeed):
        """風速設定のセッター"""
        if not isinstance(value, constants.AirconFanSpeed):
            raise ValueError("無効な風速設定です")
        self._fan_speed = value

    @property
    def power(self):
        """電源設定のプロパティ"""
        return self._power

    @power.setter
    def power(self, value: constants.AirconPower):
        """電源設定のセッター"""
        if not isinstance(value, constants.AirconPower):
            raise ValueError("無効な電源設定です")
        self._power = value

    @property
    def force_fan_below_dew_point(self):
        """露点温度を下回った場合に強制的に送風にする設定のプロパティ"""
        return self._force_fan_below_dew_point

    @force_fan_below_dew_point.setter
    def force_fan_below_dew_point(self, value: Optional[bool]):
        """露点温度を下回った場合に強制的に送風にする設定のセッター"""
        if value is not None and not isinstance(value, bool):
            raise ValueError("force_fan_below_dew_pointはbool型でなければなりません")
        self._force_fan_below_dew_point = value
