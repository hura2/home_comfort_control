from datetime import datetime

from sqlalchemy.orm import Session

from models.aircon_change_interval_model import AirconChangeIntervalModel
from shared.enums.aircon_mode import AirconMode


class AirconChangeIntervalQueries:
    """
    AirconChangeInterval テーブルに関連するクエリを実行するクラス。

    Attributes:
        session (Session): SQLAlchemyのセッションオブジェクト
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session

    def insert(
        self, mode: AirconMode, max_temperature: int, min_temperature: int, duration_minutes: int
    ) -> AirconChangeIntervalModel:
        """
        新しいエアコン設定をデータベースに挿入する。

        Args:
            mode (AirconMode): エアコンモード。
            max_temperature (int): 最高気温。
            min_temperature (int): 最低気温。
            duration_minutes (int): 最小運転時間（分）。

        Returns:
            AirconChangeIntervalModel: 新しいエアコン設定。
        """
        new_aircon_change_interval = AirconChangeIntervalModel(
            mode_id=mode.id,
            temperature_min=min_temperature,
            temperature_max=max_temperature,
            duration_minutes=duration_minutes,
        )
        self.session.add(new_aircon_change_interval)
        self.session.flush()
        return new_aircon_change_interval

    def find_by_temperature_within_range(
        self, mode: AirconMode, temperature: float
    ) -> AirconChangeIntervalModel | None:
        """
        指定されたエアコンモードと最高気温に基づいて、最小運転時間トラッカーの情報を取得します。
        
        Args:
            mode (AirconMode): 取得したいエアコンの運転モード。
            temperature (float): 対象となる気温。
        
        Returns:
            AirconChangeIntervalModel | None: 最小運転時間（分）と開始時刻のタプル。
            該当するデータが存在しない場合は None を返します。
        """
        return (
            self.session.query(AirconChangeIntervalModel)
            .filter(
                AirconChangeIntervalModel.mode_id == mode.id,
                AirconChangeIntervalModel.temperature_min <= temperature,
                AirconChangeIntervalModel.temperature_max >= temperature,
            )
            .first()
        )

    def update_start_time(self, change_interval_id: int, start_time: datetime):
        """
        最小運転時間トラッカーの開始時刻を更新します。

        Args:
            change_interval_id (int): 更新するエアコン変更間隔のID。
            start_time (datetime): 更新する開始時刻。
        """
        change_interval = (
            self.session.query(AirconChangeIntervalModel).filter_by(id=change_interval_id).first()
        )
        if change_interval is not None:
            change_interval.start_time = start_time
