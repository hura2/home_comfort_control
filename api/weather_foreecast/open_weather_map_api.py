from collections import defaultdict
from datetime import date, datetime, timezone

import requests

from api.weather_foreecast.weather_forecast_interface import WeatherForecastInterface
from logger.system_event_logger import SystemEventLogger
from settings import LOCAL_TZ
from shared.dataclass.weather_date import WeatherDate
from shared.dataclass.weather_hourly import WeatherHourly
from util.env_config_loader import EnvConfigLoader


class OpenWeatherMapApi(WeatherForecastInterface):
    """
    OpenWeatherMapのAPIを使用して気象データを取得するクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self._API_KEY = EnvConfigLoader.get_variable("OPEN_WEATHER_MAP_API_KEY")
        self._BASE_URL = EnvConfigLoader.get_variable("OPEN_WEATHER_MAP_BASE_URL")
        self._LAT = EnvConfigLoader.get_variable("OPEN_WEATHER_MAP_LAT")
        self._LON = EnvConfigLoader.get_variable("OPEN_WEATHER_MAP_LON")

    def fetch_forecast(self, start_date: date) -> list[WeatherDate]:
        """
        APIから気象データを取得して処理する
        args:
            start_date: 取得したい開始日付
        """
        weather_date_dict = defaultdict(list)  # 日付ごとにデータをグループ化する辞書

        # APIからデータを取得して処理
        for entry in self.fetch_forecast_api():
            main = entry["main"]
            wind = entry["wind"]
            weather = entry["weather"][0]
            clouds = entry["clouds"]
            utc_time = datetime.fromtimestamp(entry["dt"], timezone.utc)  # UTC時間
            local_time = utc_time.astimezone(LOCAL_TZ)  # 日本時間に変換

            # 日付（YYYY-MM-DD部分）をキーとしてグループ化
            date_key = local_time.date()  # datetime.date型で取得

            # start_date以降の日付のみ処理
            if date_key >= start_date:
                # WeatherHourlyインスタンスを作成
                weather_hourly = WeatherHourly(
                    datetime=local_time,
                    temperature=main["temp"],
                    humidity=main["humidity"],
                    pressure=main["pressure"],
                    wind_speed=wind["speed"],
                    wind_direction=wind["deg"],
                    precipitation_probability=entry["pop"],
                    weather=weather["main"],
                    cloud_percentage=int(clouds["all"]) / 100,
                )
                weather_date_dict[date_key].append(weather_hourly)

        # WeatherDateリストを生成（start_date以降の日付のみ）
        weather_date_list = []

        for date_key, hourly_list in weather_date_dict.items():
            if date_key >= start_date:
                # Pydanticモデルのインスタンスを作成
                weather_date = WeatherDate(date=date_key)
                # set_hourly_dataを明示的に呼び出して最高気温・最低気温を設定
                weather_date.set_hourly_data(hourly_list)
                # リストに追加
                weather_date_list.append(weather_date)

        return weather_date_list

    def fetch_forecast_api(self) -> dict:
        # APIリクエストのパラメータ
        params = {
            "lat": self._LAT,
            "lon": self._LON,
            "appid": self._API_KEY,
            "units": "metric",  # 摂氏: 'metric', 華氏: 'imperial', 標準: 'standard'
            "lang": "ja",  # 言語
            "cnt": 20,
        }

        try:
            # APIにリクエストを送信
            response = requests.get(self._BASE_URL + "forecast", params=params)
            response.raise_for_status()  # HTTPエラーの場合例外を発生させる

            # JSON形式でレスポンスを取得
            data = response.json()

            return data.get("list", [])

        except requests.RequestException as e:
            message = str(e)
            message = message.replace(self._API_KEY, "XXXXX")
            message = message.replace(self._LAT, "000")
            message = message.replace(self._LON, "000")
            SystemEventLogger.log_error(class_type=self.__class__, message=message)
            return {}