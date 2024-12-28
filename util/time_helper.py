from datetime import datetime

import pytz

from settings import LOCAL_TZ


class TimeHelper:
    """
    現在時刻の管理を行うクラス。

    Attributes:
        _now (datetime or None): 現在の日時情報を格納するクラス変数。初回の取得時に生成されます。
    """

    _now = None

    @staticmethod
    def get_current_time() -> datetime:
        """
        現在の日時情報を取得します。初回の呼び出し時に生成された情報を再利用します。

        Returns:
            datetime: 現在の日時情報
        """
        if TimeHelper._now is None:
            TimeHelper._now = datetime.now(LOCAL_TZ)
        return TimeHelper._now

    @staticmethod
    def parse_datetime_string(datetime_str):
        try:
            # 指定のフォーマットで文字列をパースしてタイムゾーン情報を設定
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        except Exception:
            # パース失敗時にはNoneを返す
            return None

    @staticmethod
    def calculate_elapsed_time(last_setting_time: datetime):
        # 経過時間の計算
        elapsed_time = TimeHelper.get_current_time() - last_setting_time

        # 時間と分への分割
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return hours, minutes
