from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.aircon_setting_model import AirconSettingModel
    from models.circulator_setting_model import CirculatorSettingModel
    from models.pmv_model import PmvModel
    from models.sensor_reading_model import SensorReadingModel


class MeasurementModel(Base):
    """計測日時"""
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    measurement_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """計測日時"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""
    # Relationships
    sensor_readings: Mapped["SensorReadingModel"] = relationship("SensorReadingModel", back_populates="measurement")  # type: ignore
    """センサー計測結果"""
    pmv_calculations: Mapped["PmvModel"] = relationship("PmvModel", back_populates="measurement")  # type: ignore
    """PMV計算結果"""
    aircon_settings: Mapped["AirconSettingModel"] = relationship("AirconSettingModel", back_populates="measurement")  # type: ignore
    """エアコン設定"""
    circulator_settings: Mapped["CirculatorSettingModel"] = relationship("CirculatorSettingModel", back_populates="measurement")  # type: ignore
    """サーキュレーター設定"""