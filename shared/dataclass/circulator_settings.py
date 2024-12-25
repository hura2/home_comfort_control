from pydantic import BaseModel, Field

from shared.enums.power_mode import PowerMode


class CirculatorSettings(BaseModel):
    """
    サーキュレーターの状態を表す Pydantic モデル。

    Attributes:
        power (PowerMode): サーキュレーターの電源設定。
        fan_speed (int): サーキュレーターの風速設定（0～最大値）。
    """

    power: PowerMode = Field(default=PowerMode.OFF, description="サーキュレーターの電源設定")
    """電源"""
    fan_speed: int = Field(default=0, ge=0, description="サーキュレーターの風速設定（0以上）")
    """風速"""

    def update_if_none(self, other: "CirculatorSettings"):
        """
        別の CirculatorSettings インスタンスの属性を基に、このインスタンスを更新します。
        None でない属性のみを更新します。

        Args:
            other (CirculatorSettings): 更新の基になる CirculatorSettings オブジェクト。
        """
        for attr_name in self.__annotations__:
            other_value = getattr(other, attr_name, None)
            if other_value is not None:
                setattr(self, attr_name, other_value)
