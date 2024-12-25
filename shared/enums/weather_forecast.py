from enum import Enum


class WeatherForecast(Enum):
    """
    天気予報サービスのタイプを定義するEnumクラス。
    """

    OPEN_WEATHER_MAP = 1
    JMA = 2