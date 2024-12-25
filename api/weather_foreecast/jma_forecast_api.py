from datetime import date, datetime

import requests

from api.weather_foreecast.weather_forecast_interface import WeatherForecastInterface
from shared.dataclass.weather_date import WeatherDate
from util.env_config_loader import EnvConfigLoader


class JmaForecastApi(WeatherForecastInterface):
    """
    JmaForecastApiクラスは、気象庁のAPIを使用して指定されたエリアの気温データを取得するためのクラスです。

    環境変数から以下の情報を取得します:
    - JMA_AREA_NAME: 取得したいエリアの名称
    - JMA_AREA_CODE: 取得したいエリアのコード

    主な機能:
    - 指定された日付の最大気温を取得するメソッド
    """

    def __init__(self):
        self._AREA_NAME = EnvConfigLoader.get_variable("JMA_AREA_NAME")
        self._AREA_CODE = EnvConfigLoader.get_variable("JMA_AREA_CODE")

    def fetch_forecast(self, start_date: date) -> list[WeatherDate]:
        max_temprature = self.get_max_temperature_by_date(start_date.isoformat())
        return [WeatherDate(date=start_date, max_temperature=max_temprature)]

    def get_max_temperature_by_date(self, target_date: str) -> int | None:
        """
        指定された日付の指定エリアの最大気温を取得する関数。

        :param target_date: 取得したい日付（フォーマット: 'YYYY-MM-DD'）
        :return: 最大気温 (度) または None
        """
        jma_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{self._AREA_CODE}.json"

        # セッションを使用してリクエストを管理
        with requests.Session() as session:
            try:
                response = session.get(jma_url)
                response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
                jma_json = response.json()
                print(jma_json)
            except requests.RequestException as e:
                print(f"APIリクエスト中にエラーが発生しました: {e}")
                return None

        # 指定された日付の指定エリアの最大気温を取得
        for time_series in jma_json[0]["timeSeries"]:
            time_defines = time_series.get("timeDefines", [])
            areas = time_series.get("areas", [])

            # 日付のフォーマットを統一して比較
            formatted_time_defines = [
                datetime.strptime(td, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
                for td in time_defines
            ]

            if not formatted_time_defines:
                continue

            for area_data in areas:
                if (
                    area_data["area"]["name"] == self._AREA_NAME
                ):  # 環境変数から取得したエリア名に基づく
                    temps = area_data.get("temps", [])

                    if temps:  # tempsデータがある場合
                        # 対象の日付がtimeDefinesに存在するか確認
                        if target_date in formatted_time_defines:
                            # 日付のインデックスを取得して、その日以降の気温データを抽出
                            date_index = formatted_time_defines.index(target_date)
                            subsequent_temps = temps[date_index:]  # 対象日以降の気温データを取得

                            if subsequent_temps:
                                max_temp = max(subsequent_temps, key=int)  # 最大気温を取得
                                return int(max_temp)  # 整数に変換して戻す

        return None
