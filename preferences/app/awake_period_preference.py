from datetime import time

from pydantic import BaseModel, ValidationError, field_validator

from translations.translated_pydantic_value_error import TranslatedPydanticValueError


class AwakePeriodPreference(BaseModel):
    start_time: time  # datetime.time型
    """起床時刻"""
    end_time: time  # datetime.time型
    """就寝時刻"""

    @field_validator("start_time", "end_time", mode="before")
    def validate_and_convert_time(cls, value, field):
        """
        時刻形式を検証し、strをtime型に変換します。
        """
        if isinstance(value, time):  # すでにtime型ならそのまま返す
            return value
        try:
            hour, minute = map(int, value.split(":"))
            return time(hour, minute)  # time型に変換して返す
        except Exception:
            raise TranslatedPydanticValueError(
                cls=AwakePeriodPreference,
                value=value,
            )
