import datetime
from collections import defaultdict
from typing import Optional, Tuple

import pandas as pd

import common.constants as constants
from api.jma_forecast_api import JmaForecastApi
from common.data_types import AirconState, CirculatorState, HomeSensor, Sensor
from db.supabase_client import SupabaseClient
from util.aircon_intensity_calculator import AirconIntensityCalculator
from util.time import TimeUtil


class Analytics:
    """
    Analyticsクラス
    """

    # 温度情報をデータベースに挿入
    @staticmethod
    def insert_temperature(sensor: Sensor, created_at: datetime):
        """
        温度情報をデータベースに挿入します。

        Args:
            location_id (int): 温度情報の位置ID。
            temperature (float): 温度情報。
            created_at (datetime): 温度情報の作成日時。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        id = Analytics._get_location_id(sensor.id)
        if id == -1:
            return

        result = (
            SupabaseClient.get_supabase()
            .from_("temperatures")
            .insert(
                [
                    {
                        "location_id": id,
                        "temperature": sensor.air_quality.temperature,
                        "created_at": created_at.isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # 湿度情報をデータベースに挿入
    @staticmethod
    def insert_humidity(sensor: Sensor, created_at: datetime):
        """
        湿度情報をデータベースに挿入します。

        Args:
            sensor (Sensor): 湿度情報のセンサー情報。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        id = Analytics._get_location_id(sensor.id)
        if id == -1:
            return

        result = (
            SupabaseClient.get_supabase()
            .from_("humidities")
            .insert(
                [
                    {
                        "location_id": id,
                        "humidity": sensor.air_quality.humidity,
                        "created_at": created_at.isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    @staticmethod
    def insert_co2_level(sensor: Sensor, created_at: datetime):
        """
        CO2濃度情報をデータベースに挿入します。

        Args:
            sensor (Sensor): CO2濃度情報のセンサー情報。
            created_at (datetime): CO2濃度情報の作成日時。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        id = Analytics._get_location_id(sensor.id)
        if id == -1:
            return

        result = (
            SupabaseClient.get_supabase()
            .from_("co2_levels")  # CO2濃度を格納するテーブル名
            .insert(
                [
                    {
                        "location_id": id,
                        "co2_level": sensor.air_quality.co2_level,
                        "created_at": created_at.isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # 表面温度情報をデータベースに挿入
    @staticmethod
    def insert_surface_temperature(wall_temp: float, ceiling_temp: float, floor_temp: float):
        """
        表面温度情報をデータベースに挿入します。

        Args:
            wall_temp (float): 壁の表面温度情報。
            ceiling_temp (float): 天井の表面温度情報。
            floor_temp (float): 床の表面温度情報。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        result = (
            SupabaseClient.get_supabase()
            .from_("surface_temperatures")
            .insert(
                [
                    {
                        "wall": wall_temp,
                        "ceiling": ceiling_temp,
                        "floor": floor_temp,
                        "created_at": TimeUtil.get_current_time().isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # PMV情報をデータベースに挿入

    @staticmethod
    def insert_pmv(pmv: float, met: float, clo: float, air: float):
        """
        PMV情報をデータベースに挿入します。

        Args:
            pmv (float): PMV値。
            met (float): MET値。
            clo (float): CLO値。
            air (float): 空気速度値。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        result = (
            SupabaseClient.get_supabase()
            .from_("pmvs")
            .insert(
                [
                    {
                        "pmv": pmv,
                        "met": met,
                        "clo": clo,
                        "air": air,
                        "created_at": TimeUtil.get_current_time().isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # エアコン設定情報をデータベースに挿入
    @staticmethod
    def insert_aircon_state(
        aircon_state: AirconState, current_time: Optional[datetime.datetime] = None
    ):
        """
        エアコン設定をデータベースに挿入します。

        Args:
            aircon_state (AirconState): エアコンの設定情報。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        supabase = SupabaseClient.get_supabase()
        # current_timeの設定がNoneの場合は現在の日時を設定
        if current_time is None:
            current_time = TimeUtil.get_current_time().isoformat()

        data = {
            "temperature": aircon_state.temperature,
            "mode": aircon_state.mode.id,
            "fan_speed": aircon_state.fan_speed.id,
            "power": aircon_state.power.id,
            "created_at": current_time,
        }

        return supabase.from_("aircon_settings").insert([data]).execute()

    # 最新のエアコン設定情報を取得
    @staticmethod
    def get_latest_aircon_state() -> Tuple[AirconState, datetime.datetime]:
        """
        最新のエアコン設定情報を取得します。

        Returns:
            Tuple[AirconState, datetime.datetime]: 最新のエアコン設定情報と作成日時のタプル。
        """
        data = (
            SupabaseClient.get_supabase()
            .table("aircon_settings")
            .select("*")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        latest_aircon_state = data.data[0]
        aircon_state = AirconState(
            temperature=str(latest_aircon_state["temperature"]),
            mode=constants.AirconMode.get_by_id(latest_aircon_state["mode"]),
            fan_speed=constants.AirconFanSpeed.get_by_id(str((latest_aircon_state["fan_speed"]))),
            power=constants.AirconPower.get_by_id(latest_aircon_state["power"]),
        )
        created_at = latest_aircon_state["created_at"]
        return aircon_state, created_at

    @staticmethod
    def insert_temperature_humidity(
        home_sensor: HomeSensor,
    ):
        """
        天井、床、外部の温度と湿度データをデータベースに挿入します。

        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
        """
        now = TimeUtil.get_current_time()
        Analytics.insert_temperature(home_sensor.main, now)
        Analytics.insert_humidity(home_sensor.main, now)
        if home_sensor.sub:
            Analytics.insert_temperature(home_sensor.sub, now)
            Analytics.insert_humidity(home_sensor.sub, now)
        for supplementary in home_sensor.supplementaries:
            Analytics.insert_temperature(supplementary, now)
            Analytics.insert_humidity(supplementary, now)
        Analytics.insert_temperature(home_sensor.outdoor, now)
        Analytics.insert_humidity(home_sensor.outdoor, now)

    @staticmethod
    def insert_co2_sensor_data(home_sensor: HomeSensor):
        """
        CO2センサーのデータをデータベースに挿入します。

        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
        """
        now = TimeUtil.get_current_time()
        if home_sensor.main.type == constants.SensorType.CO2:
            Analytics.insert_co2_level(home_sensor.main, now)
        if home_sensor.sub and home_sensor.sub.type == constants.SensorType.CO2:
            Analytics.insert_co2_level(home_sensor.sub, now)
        for supplementary in home_sensor.supplementaries:
            if supplementary.type == constants.SensorType.CO2:
                Analytics.insert_co2_level(supplementary, now)

    # サーキュレーター設定情報をデータベースに挿入
    @staticmethod
    def insert_circulator_state(circulator_state: CirculatorState):
        """
        サーキュレーターの風速と電源設定をデータベースに挿入します。

        Args:
            circulator_state (CirculatorState): サーキュレーターの風速と電源設定

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        result = (
            SupabaseClient.get_supabase()
            .from_("circulator_settings")
            .insert(
                [
                    {
                        "fan_speed": str(circulator_state.fan_speed),
                        "power": circulator_state.power.description,
                        "created_at": TimeUtil.get_current_time().isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # 最新のサーキュレーター設定情報を取得
    @staticmethod
    def get_latest_circulator_state() -> CirculatorState:
        """
        最新のサーキュレーターの風速と電源設定を取得します。

        Returns:
            CirculatorState: 最新のサーキュレーターの設定情報
        """
        data = (
            SupabaseClient.get_supabase()
            .table("circulator_settings")
            .select("power, fan_speed")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return CirculatorState(
            power=constants.CirculatorPower.get_by_description(data.data[0]["power"]),
            fan_speed=int(data.data[0]["fan_speed"]),
        )

    # 日毎の最高気温をデータベースに挿入
    @staticmethod
    def insert_max_temperature(max_temperature: float):
        """
        日毎の最高気温をデータベースに挿入します。

        Args:
            recorded_date (str): 温度が記録された日付（YYYY-MM-DD形式）
            max_temperature (float): 最高気温（摂氏度）

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        result = (
            SupabaseClient.get_supabase()
            .from_("daily_max_temperatures")
            .insert(
                [
                    {
                        "recorded_date": TimeUtil.get_current_time().date().isoformat(),
                        "max_temperature": max_temperature,
                        "created_at": TimeUtil.get_current_time().isoformat(),
                    }
                ]
            )
            .execute()
        )
        return result

    # 指定した日付の最高気温を取得
    @staticmethod
    def get_max_temperature_by_date(recorded_date: str) -> Optional[Tuple[str, float]]:
        """
        指定した日付の最高気温を取得します。

        Args:
            recorded_date (str): 温度を取得したい日付（YYYY-MM-DD形式）

        Returns:
            Optional[Tuple[str, float]]: 記録日付と最高気温。データがない場合は None。
        """
        data = (
            SupabaseClient.get_supabase()
            .table("daily_max_temperatures")
            .select("recorded_date, max_temperature")
            .eq("recorded_date", recorded_date)
            .execute()
        )

        if data.data:
            return data.data[0]["recorded_date"], data.data[0]["max_temperature"]
        return None

    @staticmethod
    def get_or_insert_max_temperature() -> float:
        """
        現在の日付の最高気温を取得し、存在しない場合は新たに挿入します。

        Returns:
            float: 最高気温の値
        """
        # 現在の日付を取得
        recorded_date = TimeUtil.get_current_time().date().isoformat()

        # 現在の日付の最高気温を取得
        result = Analytics.get_max_temperature_by_date(recorded_date)

        # 取得できなかった場合は挿入
        if result is None:
            max_temperature = JmaForecastApi.get_max_temperature_by_date(recorded_date)
            Analytics.insert_max_temperature(max_temperature)
            return max_temperature

        # 取得できた場合は、その値を返す
        return result[1]  # 最高気温の値を返す

    # 指定した日付のエアコン設定の強度を取得
    @staticmethod
    def get_daily_aircon_intensity(date: str, calculate_last_duration: bool = True) -> int:
        """
        指定した日付のエアコン設定の強度を計算します。

        Args:
            date (str): YYYY-MM-DD形式の日付。
            calculate_last_duration (bool): 最後の設定の持続時間を計算するかどうか。

        Returns:
            int: 指定日付の強度スコア。
        """
        data = (
            SupabaseClient.get_supabase()
            .table("aircon_settings")
            .select("*")
            .filter("created_at", "gte", f"{date} 00:00:00")
            .filter("created_at", "lt", f"{date} 23:59:59")
            .execute()
        )

        intensity_by_mode = defaultdict(float)  # 各モードの強度スコアを格納
        last_setting = None

        # タイムゾーンの定義（日本時間の例）
        JST = TimeUtil.timezone()

        for setting in data.data:
            aircon_state = AirconState(
                temperature=str(setting["temperature"]),
                mode=constants.AirconMode.get_by_id(setting["mode"]),
                fan_speed=constants.AirconFanSpeed.get_by_id(str(setting["fan_speed"])),
                power=constants.AirconPower.get_by_id(setting["power"]),
            )

            created_at_str = setting["created_at"]
            created_at_str = (
                created_at_str.split(".")[0] + created_at_str[-6:]
            )  # 秒以下の部分を切り捨て
            current_time = datetime.datetime.fromisoformat(created_at_str)

            if last_setting is not None:
                # 前の設定の持続時間を計算
                time_difference = (current_time - last_setting["created_at"]).total_seconds()
                intensity_score = AirconIntensityCalculator.calculate_intensity(
                    temperature=float(last_setting["temperature"]),
                    mode=last_setting["mode"],
                    fan_speed=last_setting["fan_speed"],
                    power=last_setting["power"],
                )
                intensity_by_mode[last_setting["mode"]] += intensity_score * time_difference

            # 新しい設定を記録
            last_setting = {
                "mode": aircon_state.mode.id,
                "created_at": current_time,
                "temperature": aircon_state.temperature,
                "fan_speed": aircon_state.fan_speed.id,
                "power": aircon_state.power.id,
            }

        # 最後の設定の持続時間を計算するかどうか
        if calculate_last_duration and last_setting is not None:
            end_of_day = datetime.datetime.strptime(
                f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=JST)
            time_difference = (end_of_day - last_setting["created_at"]).total_seconds()
            intensity_score = AirconIntensityCalculator.calculate_intensity(
                temperature=float(last_setting["temperature"]),
                mode=last_setting["mode"],
                fan_speed=last_setting["fan_speed"],
                power=last_setting["power"],
            )
            intensity_by_mode[last_setting["mode"]] += intensity_score * time_difference

        # 全てのモードの強度スコアを合計
        total_intensity = sum(intensity_by_mode.values())

        return total_intensity

    @staticmethod
    def _save_intensity_score(date: str, score: int) -> None:
        """
        指定した日付とスコアをDBに保存します。

        Args:
            date (str): YYYY-MM-DD形式の日付。
            score (int): エアコン設定の強度スコア。
        """
        SupabaseClient.get_supabase().table("aircon_intensity_scores").insert(
            {"record_date": date, "intensity_score": score}
        ).execute()

    @staticmethod
    def register_yesterday_intensity_score() -> None:
        """
        昨日のエアコン強度スコアを計算し、DBに保存します。
        """
        yesterday = (TimeUtil.get_current_time() - datetime.timedelta(days=1)).date()
        date_str = yesterday.strftime("%Y-%m-%d")

        # 昨日のスコアをDBで確認
        existing_score = (
            SupabaseClient.get_supabase()
            .table("aircon_intensity_scores")
            .select("*")
            .filter("record_date", "eq", date_str)
            .execute()
        )

        # スコアが既に登録されている場合、計算をスキップ
        if existing_score.data:
            return

        # 昨日のスコアを取得
        intensity_score = Analytics.get_daily_aircon_intensity(date_str)

        # スコアをDBに保存
        Analytics._save_intensity_score(date_str, intensity_score)

        # エアコンの強度スコアを取得する関数

    @staticmethod
    def get_aircon_intensity_scores(today: datetime.date) -> Tuple[int, int, int, int, int]:
        """
        先々週、先週、今週、昨日、今日のエアコンの強度スコアを取得します。

        Args:
            today (datetime.date): 今日の日付。

        Returns:
            Tuple[int, int, int, int, int]: 先々週、先週、今週、昨日、今日のスコア。
        """

        def calculate_average_score(start_date, end_date):
            # スコア計算処理
            data = (
                SupabaseClient.get_supabase()
                .table("aircon_intensity_scores")
                .select("intensity_score")
                .filter("record_date", "gte", str(start_date))
                .filter("record_date", "lt", str(end_date))
                .execute()
            )

            total_score = sum(item["intensity_score"] for item in data.data)
            count = len(data.data)

            # 平均スコアを小数点以下切り捨てで計算
            if count > 0:
                return int(total_score // count)  # 小数点以下切り捨て
            return 0

        # 日付の計算
        yesterday = today - datetime.timedelta(days=1)
        last_week_start = today - datetime.timedelta(weeks=1, days=today.weekday())
        last_week_end = last_week_start + datetime.timedelta(days=7)
        two_weeks_ago_start = last_week_start - datetime.timedelta(days=7)
        two_weeks_ago_end = last_week_start
        this_week_start = today - datetime.timedelta(days=today.weekday())
        this_week_end = today + datetime.timedelta(days=1)

        # スコアの計算
        last_two_weeks_score = calculate_average_score(two_weeks_ago_start, two_weeks_ago_end)
        last_week_score = calculate_average_score(last_week_start, last_week_end)
        this_week_score = calculate_average_score(this_week_start, this_week_end)

        # 昨日のスコアをDBから取得
        yesterday_score_data = (
            SupabaseClient.get_supabase()
            .table("aircon_intensity_scores")
            .select("intensity_score")
            .filter("record_date", "eq", str(yesterday))
            .execute()
        )
        yesterday_score = (
            int(yesterday_score_data.data[0]["intensity_score"]) if yesterday_score_data.data else 0
        )

        # 今日のスコアを計算
        today_score = int(Analytics.get_daily_aircon_intensity(today.strftime("%Y-%m-%d"), False))

        return last_two_weeks_score, last_week_score, this_week_score, yesterday_score, today_score

    @staticmethod
    def register_last_month_intensity_scores() -> None:
        """
        過去1ヶ月の各日付のエアコン強度スコアを計算し、DBに保存します。
        """
        current_date = TimeUtil.get_current_time().date()
        start_date = current_date - datetime.timedelta(days=30)

        for i in range(30):
            target_date = start_date + datetime.timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")

            # 指定日付のスコアをDBで確認
            existing_score = (
                SupabaseClient.get_supabase()
                .table("aircon_intensity_scores")
                .select("*")
                .filter("record_date", "eq", date_str)
                .execute()
            )

            # スコアが既に登録されている場合、計算をスキップ
            if existing_score.data:
                continue

            # aircon_settingsから指定日付のデータを取得
            intensity_score = Analytics.get_daily_aircon_intensity(date_str)

            # スコアをDBに保存
            Analytics._save_intensity_score(date_str, intensity_score)
            # print(f"{date_str} のスコア {intensity_score} を登録しました。")

    @staticmethod
    def _get_location_id(sensor_id: str) -> int:
        """
        温度情報をデータベースに挿入します。

        Args:
            sensor_id (str): 温度情報の位置ID。

        Returns:
            APIResponse: 挿入結果の情報が含まれる。
        """
        data = (
            SupabaseClient.get_supabase()
            .table("locations")
            .select("id")
            .filter("sensor_id", "eq", sensor_id)
            .limit(1)
            .execute()
        )

        if not data.data:
            return -1

        return data.data[0]["id"]

    @staticmethod
    def get_hourly_average_temperature(location_id: int):
        """
        指定されたlocation_idの7時間前までのデータから、1時間ごとの平均気温を取得します。

        :param location_id: 対象とする場所のID
        :return: 各1時間ごとの平均気温（リスト）
        """
        # 現在のUTC時間と7時間前までの時間範囲を定義
        end_time = TimeUtil.get_current_time()
        start_time = end_time - datetime.timedelta(hours=6)

        # Supabaseからデータを取得
        data = (
            SupabaseClient.get_supabase()
            .table("temperatures")
            .select("created_at, temperature")
            .filter("location_id", "eq", location_id)
            .filter("created_at", "gte", start_time.isoformat())
            .filter("created_at", "lte", end_time.isoformat())
            .execute()
        )

        # DataFrameに変換し、1時間ごとの平均気温を計算
        df = pd.DataFrame(data.data)
        if df.empty:
            print("No data found for the specified location and time range.")
            return None

        # 'created_at'列をDatetime型に変換し、インデックスとして設定
        df["created_at"] = pd.to_datetime(df["created_at"])
        df.set_index("created_at", inplace=True)

        # 1時間ごとの平均気温を計算し、新しい順に並べ替えて辞書のリスト形式で返す
        hourly_avg = round(df["temperature"].resample("h").mean().dropna(), 2)
        # hourly_avg = hourly_avg.iloc[::-1]  # 新しい順に並べ替え

        # 結果をリスト形式で返す（辞書で時間ごとのデータを保持）
        return (
            hourly_avg.reset_index()
            .rename(columns={"created_at": "hour", "temperature": "average_temperature"})
            .to_dict(orient="records")
        )
