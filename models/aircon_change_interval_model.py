from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.aircon_mode_model import AirconModeModel


class AirconChangeIntervalModel(Base):
    """エアコン変更間隔"""
    __tablename__ = "aircon_change_intervals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    mode_id: Mapped[int] = mapped_column(ForeignKey("aircon_modes.id"), nullable=False)
    """モードID"""
    temperature_min: Mapped[float] = mapped_column(Float, nullable=False)
    """最低温度"""
    temperature_max: Mapped[float] = mapped_column(Float, nullable=False)
    """最高温度"""
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    """間隔時間(分)"""
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """開始時間"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )

    # Composite Primary Key
    __table_args__ = (UniqueConstraint("mode_id", "temperature_min", "temperature_max"),)

    # Relationship to AirconMode
    mode: Mapped["AirconModeModel"] = relationship(
        "AirconModeModel", back_populates="aircon_change_intervals"
    )
