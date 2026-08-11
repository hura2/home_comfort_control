from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.measurement_model import MeasurementModel


class ElectricFanSettingModel(Base):
    """扇風機設定"""

    __tablename__ = "electric_fan_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id"), nullable=False)
    """計測日時ID"""
    fan_speed: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    """扇風機の風量"""
    power: Mapped[str] = mapped_column(Text, nullable=False)
    """電源"""
    rhythm: Mapped[str] = mapped_column(Text, nullable=False)
    """リズム風"""
    swing: Mapped[str] = mapped_column(Text, nullable=False)
    """左右首振り"""
    vertical_swing: Mapped[str] = mapped_column(Text, nullable=False)
    """上下首振り"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""

    # Relationship to Measurement
    measurement: Mapped["MeasurementModel"] = relationship("MeasurementModel", back_populates="electric_fan_settings")  # type: ignore
    """計測日時"""
