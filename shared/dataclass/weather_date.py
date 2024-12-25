from datetime import date

from pydantic import BaseModel, Field

from shared.dataclass.weather_hourly import WeatherHourly


class WeatherDate(BaseModel):
    """1日ごとの気象データを表現するPydanticモデル"""

    date: date  # 日付
    """日付"""
    hourly_data: list[WeatherHourly] = Field(default_factory=list)  # 時間ごとのデータ
    """時間ごとのデータ"""
    max_temperature: float | None = Field(default=None)  # 最高気温
    """最高気温"""
    min_temperature: float | None = Field(default=None)  # 最低気温
    """最低気温"""

    def set_hourly_data(self, data: list[WeatherHourly]):
        """その日の時間ごとの気象データを設定"""
        self.hourly_data = data
        # 新しいデータが設定された場合、最高気温・最低気温を計算
        if self.hourly_data:
            self.max_temperature = max(hour.temperature for hour in self.hourly_data)
            self.min_temperature = min(hour.temperature for hour in self.hourly_data)
        else:
            self.max_temperature = None
            self.min_temperature = None
