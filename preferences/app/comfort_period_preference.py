import re
from datetime import time
from typing import List

from pydantic import BaseModel, Field, field_validator

from preferences.app.time_range_preference import TimeRangePreference
from translations.translated_pydantic_value_error import TranslatedPydanticValueError
from util.weekday_helper import WeekdayHelper


class ComfortPeriodPreference(BaseModel):
    day: int
    """無効化する曜日の名称"""
    times: List[TimeRangePreference] = Field(default_factory=list)
    """無効化する時間帯のリスト (例: ["12:00-13:00"])。省略または空リストの場合はその曜日を終日有効とする"""

    @field_validator("day", mode="before")
    def validate_day_and_store_index(cls, value):
        """
        day に入る曜日名を検証して int に変換し、非公開フィールドにセットする。
        """
        index = WeekdayHelper.label_to_index(value)
        if index is None:
            raise TranslatedPydanticValueError(
                cls=ComfortPeriodPreference,
                value=value,
            )
        return index

    @field_validator("times", mode="before")
    def validate_times(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            value = [value]

        if not isinstance(value, list):
            raise TranslatedPydanticValueError(cls=ComfortPeriodPreference, value=value)

        parsed: List[dict] = []
        for item in value:
            if isinstance(item, str):
                match = re.fullmatch(r"^([01]?\d|2[0-3]):([0-5]\d)-([01]?\d|2[0-3]):([0-5]\d)$", item)
                if not match:
                    raise TranslatedPydanticValueError(cls=ComfortPeriodPreference, value=item)

                start = time(int(match.group(1)), int(match.group(2)))
                end = time(int(match.group(3)), int(match.group(4)))
                if end <= start:
                    raise TranslatedPydanticValueError(cls=ComfortPeriodPreference, value=f"{start}-{end}")

                parsed.append({
                    "start_time": start,
                    "end_time": end
                })

            elif isinstance(item, dict):
                parsed.append(item)

            elif isinstance(item, TimeRangePreference):
                parsed.append({
                    "start_time": item.start_time,
                    "end_time": item.end_time
                })

            else:
                raise TranslatedPydanticValueError(cls=TimeRangePreference, value=item)

        return parsed
