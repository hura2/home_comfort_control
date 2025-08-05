from typing import List

from pydantic import BaseModel

from preferences.app.comfort_period_preference import ComfortPeriodPreference


class ComfortControlPreference(BaseModel):

    disabled_periods: List[ComfortPeriodPreference]
    """無効化する期間設定のリスト"""
