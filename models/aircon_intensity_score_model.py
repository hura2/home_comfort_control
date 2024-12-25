from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from models import Base
from settings import LOCAL_TZ


class AirconIntensityScoreModel(Base):
    """
    エアコンの送風量を定義するテーブル。
    - 主キーとして `name` を使用し、わかりやすく管理。
    - description に送風量の説明を保持可能。
    """

    __tablename__ = "aircon_intensity_scores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""

    recode_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    """日付"""

    intensity_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    """エアコンの強度スコア"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )
    """作成日時"""
