from pydantic import BaseModel, field_validator, model_validator

from shared.enums.weather_forecast import WeatherForecast
from translations.translated_pydantic_value_error import TranslatedPydanticValueError
from translations.translated_value_error import TranslatedValueError


class WeatherForecastPreference(BaseModel):
    """WeatherForecast設定を管理するクラス"""

    type: WeatherForecast
    """WeatherForecastの種類"""

    @field_validator("type", mode="before")
    def convert_type_to_enum(cls, value, field):
        # 文字列からEnumに変換
        try:
            value = WeatherForecast[value]
        except KeyError:
            raise TranslatedPydanticValueError(
                cls=WeatherForecastPreference,
                type=value,
            )
        return value
