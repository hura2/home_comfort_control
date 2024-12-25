from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.measurement_model import MeasurementModel


class PmvModel(Base):
    """PMV計算結果"""

    __tablename__ = "pmvs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id"), nullable=False)
    """測定ID"""
    pmv: Mapped[float] = mapped_column(Float, nullable=False)  # 計算されたPMV
    """PMV"""
    # 新しく追加するフィールド
    ppd: Mapped[float] = mapped_column(Float, nullable=False)  # 不快指数 (PPD)
    """不快指数 (PPD)"""
    clo: Mapped[float] = mapped_column(Float, nullable=False)  # 衣服の断熱性 (CLO)
    """衣服の断熱性 (CLO)"""
    met: Mapped[float] = mapped_column(Float, nullable=False)  # 代謝当量 (MET)
    """代謝当量 (MET)"""
    air_speed: Mapped[float] = mapped_column(Float, nullable=False)  # 空気の速度 (m/s)
    """空気の速度 (m/s)"""
    relative_air_speed: Mapped[float] = mapped_column(Float, nullable=False)  # 相対風速 (m/s)
    """相対風速 (m/s)"""
    dynamic_clo: Mapped[float] = mapped_column(Float, nullable=False)  # 動的な衣服の断熱性 (CLO)
    """動的な衣服の断熱性 (CLO)"""
    wall_surface_temperature: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # 壁表面温度 (°C)
    """壁表面温度 (°C)"""
    mean_radiant_temperature: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # 平均放射温度 (°C)
    """平均放射温度 (°C)"""
    dry_bulb_temperature: Mapped[float] = mapped_column(Float, nullable=False)  # 乾球温度 (°C)
    """乾球温度 (°C)"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""
    # Relationship to Measurement
    measurement: Mapped["MeasurementModel"] = relationship("MeasurementModel", back_populates="pmv_calculations")  # type: ignore
    """測定"""