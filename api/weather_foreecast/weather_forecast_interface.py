from abc import ABC, abstractmethod
from datetime import date

from shared.dataclass.weather_date import WeatherDate


class WeatherForecastInterface(ABC):
    """
    WeatherForecastInterfaceは、天気予報のデータを取得するためのインターフェースを定義する抽象基底クラスです。

    このクラスは、天気予報データを取得する機能を提供するクラスによって継承されるべきです。
    - `fetch_forecast` メソッドは、指定された日の時間毎の気温や降水確率などの詳細情報を取得します。

    各メソッドは、具体的な天気予報サービスに応じて実装される必要があります。
    """

    @abstractmethod
    def fetch_forecast(self, start_date: date) -> list[WeatherDate]:
        """
        指定された日の時間毎の気温、降水確率などを取得します。

        戻り値:
            list[WeatherDate]: 時間毎の天気情報（WeatherDateオブジェクトのリスト）。

        例:
            forecast_list = fetch_forecast()
            # 取得したデータを処理する
        """
        pass
