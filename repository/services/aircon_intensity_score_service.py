from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import Tuple
from sqlalchemy.orm import Session

from models.aircon_setting_model import AirconSettingModel
from repository.queries.aircon_intensity_score_queries import AirconIntensityScoreQueries
from repository.services.aircon_setting_service import AirconSettingService
from settings import LOCAL_TZ
from util.aircon_intensity_calculator import AirconIntensityCalculator
from util.time_helper import TimeHelper


class AirconIntensityScoreService:
    """
    測定データのサービスクラス
    """

    def __init__(self, session: Session):
        """コンストラクタ"""
        # 各クエリクラスのインスタンスを初期化
        self.session = session
        self.query = AirconIntensityScoreQueries(session)

    def register_yesterday_intensity_score(self) -> None:
        """
        昨日のエアコン強度スコアを計算し、DBに保存します。
        """
        yesterday = (TimeHelper.get_current_time() - timedelta(days=1)).date()
        date_str = yesterday.strftime("%Y-%m-%d")

        # 昨日のスコアをDBで確認
        existing_score = self.query.get_score(date_str)

        # スコアが既に登録されている場合、計算をスキップ
        if existing_score:
            return

        # 昨日のスコアを取得
        intensity_score = self.get_daily_aircon_intensity(date_str)

        # スコアをDBに保存
        self.query.insert(date_str, intensity_score)

    def get_daily_aircon_intensity(self, date: str, calculate_last_duration: bool = True) -> int:
        """
        指定した日付のエアコン設定の強度を計算します。

        Args:
            date (str): YYYY-MM-DD形式の日付。
            calculate_last_duration (bool): 最後の設定の持続時間を計算するかどうか。

        Returns:
            int: 指定日付の強度スコア。
        """
        aircon_settings_service = AirconSettingService(self.session)
        aircon_settings_list = aircon_settings_service.get_aircon_settings_by_date(date)

        intensity_by_mode = defaultdict(float)  # 各モードの強度スコアを格納
        last_setting: AirconSettingModel | None = None

        for settings in aircon_settings_list:
            created_at_str = settings.created_at.isoformat()
            created_at_str = (
                created_at_str.split(".")[0] + created_at_str[-6:]
            )  # 秒以下の部分を切り捨て
            current_time = datetime.fromisoformat(created_at_str)

            if last_setting is not None:
                # 前の設定の持続時間を計算
                time_difference = (current_time - last_setting.created_at).total_seconds()
                intensity_score = AirconIntensityCalculator.calculate_intensity(
                    temperature=last_setting.temperature,
                    mode=last_setting.mode,
                    fan_speed=last_setting.fan_speed,
                    power=last_setting.power,
                )
                intensity_by_mode[last_setting.mode.id] += intensity_score * time_difference

            # 新しい設定を記録
            last_setting = AirconSettingModel(
                mode_id=settings.mode.id,
                temperature=settings.temperature,
                fan_speed_id=settings.fan_speed.id,
                power=settings.power,
            )

        # 最後の設定の持続時間を計算するかどうか
        if calculate_last_duration and last_setting is not None:
            end_of_day = datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=LOCAL_TZ
            )
            time_difference = (end_of_day - last_setting.created_at).total_seconds()
            intensity_score = AirconIntensityCalculator.calculate_intensity(
                temperature=last_setting.temperature,
                mode=last_setting.mode,
                fan_speed=last_setting.fan_speed,
                power=last_setting.power,
            )
            intensity_by_mode[last_setting.mode.id] += intensity_score * time_difference

        # 全てのモードの強度スコアを合計
        total_intensity = sum(intensity_by_mode.values())

        return int(total_intensity)

    def get_aircon_intensity_scores(self, today: date) -> tuple[int, int, int, int, int]:
        """
        先々週、先週、今週、昨日、今日のエアコンの強度スコアを取得します。

        Args:
            today (date): 今日の日付。

        Returns:
            Tuple[int, int, int, int, int]: 先々週、先週、今週、昨日、今日のスコア。
        """

        def calculate_average_score(start_date, end_date):
            # スコア計算処理
            data = self.query.get_intensity_scores_by_date_range(start_date, end_date)
            total_score = sum(item.intensity_score for item in data)
            count = len(data)

            # 平均スコアを小数点以下切り捨てで計算
            if count > 0:
                return int(total_score // count)  # 小数点以下切り捨て
            return 0

        # 日付の計算
        yesterday = today - timedelta(days=1)
        last_week_start = today - timedelta(weeks=1, days=today.weekday())
        last_week_end = last_week_start + timedelta(days=7)
        two_weeks_ago_start = last_week_start - timedelta(days=7)
        two_weeks_ago_end = last_week_start
        this_week_start = today - timedelta(days=today.weekday())
        this_week_end = today + timedelta(days=1)

        # スコアの計算
        last_two_weeks_score = calculate_average_score(two_weeks_ago_start, two_weeks_ago_end)
        last_week_score = calculate_average_score(last_week_start, last_week_end)
        this_week_score = calculate_average_score(this_week_start, this_week_end)

        # 昨日のスコアをDBから取得
        yesterday_score_data = self.query.get_score(yesterday.strftime("%Y-%m-%d"))
        yesterday_score = (
            int(yesterday_score_data.intensity_score) if yesterday_score_data else 0
        )

        # 今日のスコアを計算
        today_score = int(self.get_daily_aircon_intensity(today.strftime("%Y-%m-%d"), False))

        return last_two_weeks_score, last_week_score, this_week_score, yesterday_score, today_score
