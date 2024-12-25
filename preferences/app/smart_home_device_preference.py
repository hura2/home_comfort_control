from pydantic import BaseModel, field_validator

from shared.enums.smart_home_device import SmartHomeDevice
from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class SmartHomeDevicePreference(BaseModel):
    """SmartDevice設定を管理するクラス"""

    device_type: SmartHomeDevice
    """SmartDeviceの種類"""

    @field_validator("device_type", mode="before")
    def convert_type_to_enum(cls, value, field):
        # 文字列からEnumに変換
        try:
            value = SmartHomeDevice[value]
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=SmartHomeDevicePreference,
                type=value,
            )
        return value
