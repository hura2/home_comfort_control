from datetime import time

from pydantic import BaseModel


class TimeRangePreference(BaseModel):
    """
    開始時刻と終了時刻を保持する時間帯クラス。
    """

    start_time: time
    end_time: time
