from datetime import datetime

from sqlalchemy.orm import Session

from api.weather_foreecast.weather_forecast_factory import WeatherForecastFactory
from repository.queries.weather_forecast_queries import WeatherForecastQueries
from repository.services.weather_forecast_hourly_service import WeatherForecastHourlyService
from shared.dataclass.weather_date import WeatherDate
from util.time_helper import TimeHelper


class WeatherForecastService:
    """
    天気予報を管理するビジネスロジッククラス
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session
        self.query = WeatherForecastQueries(session)

    def get_max_temperature(self) -> float:
        """
        現在の日付の最高気温を取得し、存在しない場合は新たに挿入します。

        Returns:
            float: 最高気温の値
        """
        # 現在の日付を取得
        recorded_date = TimeHelper.get_current_time().date().isoformat()

        # 現在の日付の最高気温を取得
        result = self.query.get_by_forecast_date(recorded_date)

        # 取得できた場合は、その値を返す
        return result.max_temperature  # 最高気温の値を返す

    def upsert_with_hourly(self, start_date: datetime):
        """
        今日の最高気温と最低気温を取得し、存在しない場合は新たに挿入します。

        Args:
            target_date (datetime): 今日の日付
        """
        # APIを使用して、今日の最高気温と最低気温を取得
        weather_forecast = WeatherForecastFactory().create_forecast()
        forecast_date_list: list[WeatherDate] = weather_forecast.fetch_forecast(start_date.date())
        weather_forecast_hourly_service = WeatherForecastHourlyService(self.session)

        for forecast_date in forecast_date_list:
            weather_forecast_model = self.query.get_by_forecast_date(forecast_date.date.isoformat())
            if weather_forecast_model is None:
                # 今日の最高気温と最低気温を新規に挿入
                weather_forecast_model = self.query.insert(
                    forecast_date.date.isoformat(),
                    forecast_date.max_temperature,
                    forecast_date.min_temperature,
                )
                self.session.flush()
            else:
                # 今日の最高気温と最低気温を更新
                temp_max = max(
                    forecast_date.max_temperature or float("-inf"),
                    weather_forecast_model.max_temperature,
                )
                if weather_forecast_model.max_temperature != temp_max:
                    weather_forecast_model.max_temperature = temp_max
                if weather_forecast_model.min_temperature is not None:
                    temp_min = min(
                        forecast_date.min_temperature or float("inf"),
                        weather_forecast_model.min_temperature,
                    )
                    if weather_forecast_model.min_temperature != temp_min:
                        weather_forecast_model.min_temperature = temp_min

            # 今日の時間別の気温を取得
            for forecast_hourly in forecast_date.hourly_data:
                # 予報の時間帯（HH:MM:SS）を基に、同じ時間帯のデータを取得
                weather_forecast_hourly_model = (
                    weather_forecast_hourly_service.get_by_forecast_time(forecast_hourly.datetime)
                )
                if weather_forecast_hourly_model is None:
                    # 今日の時間別の気温を新規に挿入
                    weather_forecast_hourly_service.insert(
                        weather_forecast_id=weather_forecast_model.id,
                        weather_hourly=forecast_hourly,
                    )
                    self.session.flush()
                else:
                    # 今日の時間別の気温を更新
                    weather_forecast_hourly_model.temperature = forecast_hourly.temperature  # 気温
                    weather_forecast_hourly_model.humidity = forecast_hourly.humidity  # 湿度
                    weather_forecast_hourly_model.pressure = forecast_hourly.pressure  # 気圧
                    weather_forecast_hourly_model.wind_speed = forecast_hourly.wind_speed  # 風速
                    weather_forecast_hourly_model.wind_direction = (
                        forecast_hourly.wind_direction
                    )  # 風向
                    weather_forecast_hourly_model.precipitation_probability = (
                        forecast_hourly.precipitation_probability
                    )  # 降水確率
                    weather_forecast_hourly_model.weather = forecast_hourly.weather  # 天気
                    weather_forecast_hourly_model.cloud_percentage = (
                        forecast_hourly.cloud_percentage
                    )  # 雲量
