from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models.sensor_model import SensorModel


class SensorTypeModel(Base):
    """
    センサーの種類を格納するマスター用テーブルのモデル。
    """

    __tablename__ = "sensor_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    """センサーの種類名"""

    sensors: Mapped[list["SensorModel"]] = relationship("SensorModel", back_populates="sensor_type")  # type: ignore
    """センサー"""

    __table_args__ = (UniqueConstraint("name", name="uq_sensor_type_name"),)
