from api.weather_foreecast.jma_forecast_api import JmaForecastApi
from api.weather_foreecast.open_weather_map_api import OpenWeatherMapApi
from api.weather_foreecast.weather_forecast_interface import WeatherForecastInterface
from settings import app_preference
from shared.enums.weather_forecast import WeatherForecast


class WeatherForecastFactory:
    """
    天気予報を生成するファクトリクラス。
    """

    @classmethod
    def create_forecast(cls) -> WeatherForecastInterface:
        """
        天気予報を生成するファクトリーメソッド。

        設定ファイルからAPIの種類を取得し、その種類に基づいて
        対応する天気予報インスタンスを生成して返す。

        Returns:
            WeatherForecastInterface: 生成された天気予報のインスタンス。
        """
        if app_preference.weather_forecast.type == WeatherForecast.OPEN_WEATHER_MAP:
            return OpenWeatherMapApi()  # OpenWeatherMapAPIのインスタンスを返す
        if app_preference.weather_forecast.type == WeatherForecast.JMA:
            return JmaForecastApi()

        return JmaForecastApi()
