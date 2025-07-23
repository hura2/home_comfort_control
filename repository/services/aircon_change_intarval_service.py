from datetime import datetime
from typing import Tuple

from sqlalchemy.orm import Session

from repository.queries.aircon_change_intarval_queries import AirconChangeIntervalQueries
from shared.enums.aircon_mode import AirconMode
from util.time_helper import TimeHelper


class AirconChangeIntarvalService:
    """
    エアコン設定を管理するビジネスロジッククラス。

    エアコン設定の挿入や更新などのビジネスロジックを担当します。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session
        self.query = AirconChangeIntervalQueries(session)

    def update_start_time_if_exists(self, mode: AirconMode, temperature: float):
        """
        最新のエアコン設定情報を取得します。

        Returns:
            AirconSettings: 最新のエアコン設定情報
        """
        aircon_change_interval = self.query.find_by_temperature_within_range(mode, temperature)
        if aircon_change_interval:
            self.query.update_start_time(aircon_change_interval.id, TimeHelper.get_current_time())

    def get_aircon_min_runtime_tracker_for_conditions(
        self, mode: AirconMode, max_temperature: float
    ) -> Tuple[int | None, datetime | None]:
        """
        指定されたエアコンモードと最高気温に基づいて、最小運転時間トラッカーの情報を取得します。

        Args:
            mode (AirconMode): 取得したいエアコンの運転モード。
            max_temperature (float): 対象となる最高気温。

        Returns:
            Tuple[int | None, datetime | None]: 最小運転時間（分）と開始時刻のタプル。
            該当するデータが存在しない場合は None を返します。
        """
        aircon_change_interval = self.query.find_by_temperature_within_range(mode, max_temperature)

        if not aircon_change_interval:
            return None, None

        return aircon_change_interval.duration_minutes, aircon_change_interval.start_time
