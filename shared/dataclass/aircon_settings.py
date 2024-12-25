from pydantic import BaseModel, Field, field_validator

from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from shared.enums.power_mode import PowerMode
from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class AirconSettings(BaseModel):
    """
    エアコンの設定を表すクラス。

    Attributes:
        temperature (float): 温度設定。
        mode (AirconMode): 動作モード設定（エアコンモード）。
        fan_speed (AirconFanSpeed): 風速設定。
        power (PowerMode): 電源設定。
        force_fan_below_dew_point (bool): 露点温度を下回った場合に強制的に送風にするかどうかの設定。
    """

    temperature: float = Field(default=20.0, ge=18, le=30, description="温度設定")
    mode: AirconMode = Field(default=AirconMode.FAN, description="動作モード設定")
    fan_speed: AirconFanSpeed = Field(default=AirconFanSpeed.AUTO, description="風速設定")
    power: PowerMode = Field(default=PowerMode.ON, description="電源設定")
    force_fan_below_dew_point: bool = Field(
        default=False, description="露点温度を下回った場合に強制的に送風にする設定"
    )

    # class Config:
    #     use_enum_values = True
    #     arbitrary_types_allowed = True

    @field_validator("mode", mode="before")
    def convert_mode_to_enum(cls, value, field):
        """modeを文字列からEnumに変換する"""
        try:
            if isinstance(value, AirconMode):
                return value
            value = AirconMode[value]
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=AirconSettings,
                mode=value,
            )
        return value

    @field_validator("fan_speed", mode="before")
    def convert_fan_speed_to_enum(cls, value, field):
        """fan_speedを文字列からEnumに変換する"""
        try:
            if isinstance(value, AirconFanSpeed):
                return value
            value = AirconFanSpeed[value]
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=AirconSettings,
                fan_speed=value,
            )
        return value

    @field_validator("power", mode="before")
    def convert_power_to_enum(cls, value, field):
        """powerを文字列からEnumに変換する"""
        try:
            if isinstance(value, PowerMode):
                return value
            if value == True:
                value = PowerMode.ON
            elif value == False:
                value = PowerMode.OFF
            else:
                raise TranslatedPydanticValueError(
                    cls=AirconSettings,
                    power=value,
                )
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=AirconSettings,
                power=value,
            )
        return value

    def update_if_none(self, other: "AirconSettings"):
        """
        別のAirconSettingsインスタンスの属性を基に、このインスタンスを更新します。
        Noneでない属性のみを更新します。

        Args:
            other (AirconSettings): 更新の基になるAirconSettingsオブジェクト。
        """
        for attr_name in vars(self):  # dataclasses.fieldsは不要
            other_value = getattr(other, attr_name)
            if other_value is not None:
                setattr(self, attr_name, other_value)


# from typing import Optional

# from shared.enums.aircon_fan_speed import AirconFanSpeed
# from shared.enums.aircon_mode import AirconMode
# from shared.enums.power_mode import PowerMode


# class AirconSettings:
#     """
#     エアコンの設定を表すクラス。

#     Attributes:
#         temperature (str): 温度設定。
#         mode (constants.AirconMode): 動作モード設定（エアコンモード）。
#         fan_speed (constants.AirconFanSpeed): 風速設定。
#         power (constants.AirconPower): 電源設定。
#         force_fan_below_dew_point (Optional[bool]): 露点温度を下回った場合に強制的に送風にするかどうかの設定。
#     """

#     def __init__(
#         self,
#         temperature: str = "20",
#         mode: AirconMode = AirconMode.FAN,
#         fan_speed: AirconFanSpeed = AirconFanSpeed.AUTO,
#         power: PowerMode = PowerMode.ON,
#         force_fan_below_dew_point: Optional[bool] = False,
#     ):
#         self.temperature = temperature
#         self.mode = mode
#         self.fan_speed = fan_speed
#         self.power = power
#         self.force_fan_below_dew_point = force_fan_below_dew_point

#     def __eq__(self, other):
#         """
#         他のAirconStateオブジェクトと比較して、等しいかどうかを判定するメソッド。

#         Args:
#             other: 比較対象のオブジェクト。

#         Returns:
#             bool: オブジェクトが等しい場合はTrue、そうでない場合はFalse。
#         """
#         if isinstance(other, AirconSettings):
#             return (
#                 self._temperature == other._temperature
#                 and self._mode == other._mode
#                 and self._fan_speed == other._fan_speed
#                 and self._power == other._power
#             )
#         return False

#     def update_if_none(self, other):
#         """
#         別のAirconStateインスタンスの属性を基に、このインスタンスを更新します。
#         Noneでない属性のみを更新します。

#         Args:
#             other (AirconState): 更新の基になるAirconStateオブジェクト。
#         """
#         if not isinstance(other, AirconSettings):
#             raise TypeError("更新対象はAirconState型である必要があります。")

#         for attr_name in vars(self):  # dataclasses.fieldsは不要
#             other_value = getattr(other, attr_name)
#             if other_value is not None:
#                 setattr(self, attr_name, other_value)

#     @property
#     def temperature(self):
#         """温度設定のプロパティ"""
#         return self._temperature

#     @temperature.setter
#     def temperature(self, value: float):
#         """温度設定のセッター"""
#         self._temperature = value

#     @property
#     def mode(self):
#         """動作モード設定のプロパティ"""
#         return self._mode

#     @mode.setter
#     def mode(self, value: AirconMode):
#         """動作モード設定のセッター"""
#         self._mode = value

#     @property
#     def fan_speed(self):
#         """風速設定のプロパティ"""
#         return self._fan_speed

#     @fan_speed.setter
#     def fan_speed(self, value: AirconFanSpeed):
#         """風速設定のセッター"""
#         self._fan_speed = value

#     @property
#     def power(self):
#         """電源設定のプロパティ"""
#         return self._power

#     @power.setter
#     def power(self, value: PowerMode):
#         """電源設定のセッター"""
#         self._power = value

#     @property
#     def force_fan_below_dew_point(self):
#         """露点温度を下回った場合に強制的に送風にする設定のプロパティ"""
#         return self._force_fan_below_dew_point

#     @force_fan_below_dew_point.setter
#     def force_fan_below_dew_point(self, value: Optional[bool]):
#         """露点温度を下回った場合に強制的に送風にする設定のセッター"""
#         self._force_fan_below_dew_point = value
