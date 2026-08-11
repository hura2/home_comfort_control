from pydantic import BaseModel, Field

from shared.enums.power_mode import PowerMode


class ElectricFanSettings(BaseModel):
    """
    扇風機の状態を表す Pydantic モデル。

    Attributes:
        power (PowerMode): 扇風機の電源設定。
        fan_speed (int): 扇風機の風速設定（0～最大値）。
    """

    power: PowerMode = Field(default=PowerMode.OFF, description="扇風機の電源設定")
    """電源"""
    fan_speed: int = Field(default=0, ge=0, description="扇風機の風速設定（0以上）")
    """風速"""
    swing: PowerMode = Field(default=PowerMode.OFF, description="扇風機のスイング")
    """スイング"""
    vertical_swing: PowerMode = Field(default=PowerMode.OFF, description="垂直扇風機のスイング")
    """垂直扇風機のスイング"""
    rhythm: PowerMode = Field(default=PowerMode.OFF, description="リズム")
    """リズム"""

    def update_if_none(self, other: "ElectricFanSettings"):
        """
        別の ElectricFanSettings インスタンスの属性を基に、このインスタンスを更新します。
        None でない属性のみを更新します。

        Args:
            other (ElectricFanSettings): 更新の基になる ElectricFanSettings オブジェクト。
        """
        for attr_name in self.__annotations__:
            other_value = getattr(other, attr_name, None)
            if other_value is not None:
                setattr(self, attr_name, other_value)
