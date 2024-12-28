from sqlalchemy.orm import Session

from models.weather_forecast_hourly_model import WeatherForecastHourlyModel


class WeatherForecastHourlyQueries:
    """
    天気予報時間単位情報を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(
        self,
        weather_forecast_id: int,
        forecast_time: str,
        temperature: float,
        humidity: float | None = None,
        pressure: int | None = None,
        wind_speed: float | None = None,
        wind_direction: int | None = None,
        precipitation_probability: float | None = None,
        weather: str | None = None,
        cloud_percentage: float | None = None,
    ) -> WeatherForecastHourlyModel:
        """
        時間単位の天気予報を新規に挿入する。

        Args:
            weather_forecast_id (int): 天気予報ID
            forecast_time (str): 天気予報の日付と時刻      
            temperature (float): 気温
            humidity (float | None): 湿度
            pressure (int | None):気圧
            wind_speed (float | None):風速
            wind_direction (int | None):風向
            precipitation_probability (float | None):降水確率
            weather (str | None):天気
            cloud_percentage (float | None):雲量

        Returns:
            WeatherForecastHourlyModel: 新しく挿入された天気予報
        """
        new_weather_forecast_hourly = WeatherForecastHourlyModel(
            weather_forecast_id=weather_forecast_id,
            forecast_time=forecast_time,
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            precipitation_probability=precipitation_probability,
            weather=weather,
            cloud_percentage=cloud_percentage,
        )
        self.session.add(new_weather_forecast_hourly)
        self.session.flush()
        return new_weather_forecast_hourly

    def get_by_forecast_time(self, forecast_time: str) -> WeatherForecastHourlyModel:
        """
        時間単位の天気予報を取得する。

        Args:
            forecast_time (str): 天気予報の日付と時刻

        Returns:
            WeatherForecastHourlyModel: 天気予報
        """
        return (
            self.session.query(WeatherForecastHourlyModel)
            .filter_by(forecast_time=forecast_time)
            .first()
        )
    
    def get_closest_forecast_after(self, forecast_time: str) -> WeatherForecastHourlyModel:
        """
        指定された日時を含まず、それ以降で直近の天気予報を取得する。

        Args:
            forecast_time (str): 天気予報の日付と時刻

        Returns:
            WeatherForecastHourlyModel: 指定された日時を含まない直近の天気予報
        """
        return (
            self.session.query(WeatherForecastHourlyModel)
            .filter(WeatherForecastHourlyModel.forecast_time > forecast_time)  # 指定日時「以降」ではなく「後」
            .order_by(WeatherForecastHourlyModel.forecast_time.asc())          # 日時で昇順にソート
            .first()                                                           # 最初のデータを取得
        )

