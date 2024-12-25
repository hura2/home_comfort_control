from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.measurement_model import MeasurementModel
    from models.sensor_model import SensorModel


class SensorReadingModel(Base):
    """センサー計測結果"""
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id"), nullable=False)
    """測定結果"""
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"), nullable=False)
    """センサー"""
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    """温度"""
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    """湿度"""
    co2_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    """CO2濃度"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""
    measurement: Mapped["MeasurementModel"] = relationship("MeasurementModel", back_populates="sensor_readings")  # type: ignore
    """測定結果"""
    sensor: Mapped["SensorModel"] = relationship("SensorModel", back_populates="sensor_readings")  # type: ignore
    """センサー"""