from sqlalchemy.orm import Session

from models.weather_forecast_model import WeatherForecastModel


class WeatherForecastQueries:
    """
    天気予報を管理するクエリクラス。
    """
    def __init__(self, session: Session):
        """コンストラクタ"""
        self.session = session

    def insert(
        self, forecast_date: str, max_temperature: float | None, min_temperature: float | None
    ) -> WeatherForecastModel:
        """
        新しい天気予報をデータベースに挿入する。

        Args:
            forecast_date (str): 天気予報の日付
            max_temperature (float | None): 最高気温
            min_temperature (float | None): 最低気温

        Returns:
            WeatherForecastModel: 挿入された天気予報のインスタンス
        """
        new_weather_forecast = WeatherForecastModel(
            forecast_date=forecast_date,
            max_temperature=max_temperature,
            min_temperature=min_temperature,
        )
        self.session.add(new_weather_forecast)
        self.session.flush()
        return new_weather_forecast

    def get_by_forecast_date(self, forecast_date: str) -> WeatherForecastModel:
        """
        指定した日付の天気予報を取得する。

        Args:
            forecast_date (str): 天気予報の日付

        Returns:
            WeatherForecastModel: 天気予報のインスタンス
        """
        return (
            self.session.query(WeatherForecastModel).filter_by(forecast_date=forecast_date).first()
        )
