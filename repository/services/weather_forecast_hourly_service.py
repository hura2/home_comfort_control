from datetime import datetime

from sqlalchemy.orm import Session

from models.weather_forecast_hourly_model import WeatherForecastHourlyModel
from repository.queries.weather_forecast_hourly_queries import WeatherForecastHourlyQueries
from settings import LOCAL_TZ
from shared.dataclass.weather_hourly import WeatherHourly
from util.time_helper import TimeHelper


class WeatherForecastHourlyService:
    """
    時間単位の天気予報を管理するビジネスロジッククラス。

    天気予報の挿入や更新などのビジネスロジックを担当します。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session
        self.query = WeatherForecastHourlyQueries(session)

    def insert(
        self,
        weather_forecast_id: int,
        weather_hourly: WeatherHourly,
    ) -> WeatherForecastHourlyModel:
        """
        時間単位の天気予報を新規に挿入する。

        Args:
            weather_forecast_id (int): 天気予報ID
            weather_hourly (WeatherHourly): 気象情報

        Returns:
            WeatherForecastHourlyModel: 新しく挿入された天気予報
        """
        # タイムゾーンを持っていない datetime ならば localize を使ってタイムゾーンを設定
        if weather_hourly.datetime.tzinfo is None:
            # datetime 型でタイムゾーン情報がない場合、LOCAL_TZにローカライズ
            local_time = LOCAL_TZ.localize(weather_hourly.datetime)
        else:
            # タイムゾーン情報がすでに含まれている場合、そのまま使用
            local_time = weather_hourly.datetime

        return self.query.insert(
            weather_forecast_id=weather_forecast_id,  # 外部キー
            forecast_time=local_time.isoformat(),  # 日付と時刻
            temperature=weather_hourly.temperature,  # 気温
            humidity=weather_hourly.humidity,  # 湿度
            pressure=weather_hourly.pressure,  # 気圧
            wind_speed=weather_hourly.wind_speed,  # 風速
            wind_direction=weather_hourly.wind_direction,  # 風向
            precipitation_probability=weather_hourly.precipitation_probability,  # 降水確率
            weather=weather_hourly.weather,  # 天気
            cloud_percentage=weather_hourly.cloud_percentage,  # 雲量
        )

    def get_by_forecast_time(self, forecast_time: datetime) -> WeatherForecastHourlyModel:
        """
        時間単位の天気予報を取得する。

        Args:
            forecast_time (datetime): 天気予報の日付と時刻

        Returns:
            WeatherForecastHourlyModel: 天気予報
        """
        return self.query.get_by_forecast_time(forecast_time.isoformat())

    def get_closest_future_forecast(self) -> WeatherForecastHourlyModel:
        """
        指定された日時を含まず、それ以降で直近の天気予報を取得する。


        Returns:
            WeatherForecastHourlyModel: 直近の天気予報
        """
        return self.query.get_closest_forecast_after(TimeHelper.get_current_time().isoformat())
