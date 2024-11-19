from common import constants
from typing import Optional

class CirculatorState:
    """
    サーキュレーターの状態を表すクラス。

    Attributes:
        power (constants.CirculatorPower): サーキュレーターの電源設定。
        fan_speed (int): サーキュレーターの風速設定（0～最大値）。
    """

    def __init__(
        self,
        power: constants.CirculatorPower = constants.CirculatorPower.OFF,
        fan_speed: int = 0,
    ):
        self.power = power
        self.fan_speed = fan_speed

    def __eq__(self, other):
        """
        他のCirculatorStateオブジェクトと比較して、等しいかどうかを判定するメソッド。

        Args:
            other: 比較対象のオブジェクト。

        Returns:
            bool: オブジェクトが等しい場合はTrue、そうでない場合はFalse。
        """
        if isinstance(other, CirculatorState):
            return self._power == other._power and self._fan_speed == other._fan_speed
        return False

    def update_if_none(self, other):
        """
        別のCirculatorStateインスタンスの属性を基に、このインスタンスを更新します。
        Noneでない属性のみを更新します。

        Args:
            other (CirculatorState): 更新の基になるCirculatorStateオブジェクト。
        """
        if not isinstance(other, CirculatorState):
            raise TypeError("更新対象はCirculatorState型である必要があります。")

        for attr_name in vars(self):
            other_value = getattr(other, attr_name)
            if other_value is not None:
                setattr(self, attr_name, other_value)

    @property
    def power(self):
        """サーキュレーターの電源設定のプロパティ"""
        return self._power

    @power.setter
    def power(self, value: constants.CirculatorPower):
        """サーキュレーターの電源設定のセッター"""
        if not isinstance(value, constants.CirculatorPower):
            raise ValueError("無効なサーキュレーターの電源設定です")
        self._power = value

    @property
    def fan_speed(self):
        """サーキュレーターの風速設定のプロパティ"""
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, value: int):
        """サーキュレーターの風速設定のセッター"""
        if not isinstance(value, int) or value < 0:
            raise ValueError("風速は0以上の整数でなければなりません")
        self._fan_speed = value
