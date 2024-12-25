from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.aircon_fan_speed_model import AirconFanSpeedModel
    from models.aircon_mode_model import AirconModeModel
    from models.measurement_model import MeasurementModel


class AirconSettingModel(Base):
    """エアコン設定"""

    __tablename__ = "aircon_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id"), nullable=False)
    """計測日時ID"""
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    """温度"""
    mode_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("aircon_modes.id"), nullable=False
    )
    """モード"""
    fan_speed_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("aircon_fan_speeds.id"), nullable=False
    )
    """送風"""

    power: Mapped[str] = mapped_column(Text, nullable=False)
    """電源"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""
    # Relationship to Measurement
    measurement: Mapped["MeasurementModel"] = relationship(
        "MeasurementModel", back_populates="aircon_settings"
    )
    """計測"""
    # Relationship to AirconMode
    mode: Mapped["AirconModeModel"] = relationship(
        "AirconModeModel", back_populates="aircon_settings"
    )
    """モード"""
    # Relationship to AirconFanSpeed
    fan_speed: Mapped["AirconFanSpeedModel"] = relationship(
        "AirconFanSpeedModel", back_populates="aircon_settings"
    )
    """送風量"""
