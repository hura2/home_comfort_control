from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from models.aircon_intensity_score_model import AirconIntensityScoreModel
from models.measurement_model import MeasurementModel
from util.time_helper import TimeHelper


class AirconIntensityScoreQueries:
    """
    測定日時を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def get_score(self, recode_date: str) -> AirconIntensityScoreModel | None:
        return (
            self.session.query(AirconIntensityScoreModel)
            .filter(AirconIntensityScoreModel.recode_date == recode_date)
            .one_or_none()
        )

    def insert(self, date: str, score: int) -> AirconIntensityScoreModel:
        """
        指定した日付とスコアをDBに保存します。

        Args:
            date (str): YYYY-MM-DD形式の日付。
            score (int): エアコン設定の強度スコア。
        """
        aircon_intensity_score = AirconIntensityScoreModel(recode_date=date, intensity_score=score)
        self.session.add(aircon_intensity_score)
        self.session.flush()
        return aircon_intensity_score

    def get_intensity_scores_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[AirconIntensityScoreModel]:
        """
        指定した日付範囲のエアコン強度スコアを取得する。

        :param start_date: 開始日（例: date(2024, 12, 24)）
        :param end_date: 終了日（例: date(2024, 12, 25)）
        :return: エアコン強度スコアモデルのリスト
        """
        return (
            self.session.query(AirconIntensityScoreModel)
            .filter(
                AirconIntensityScoreModel.recode_date >= start_date,
                AirconIntensityScoreModel.recode_date < end_date,
            )
            .all()
        )
