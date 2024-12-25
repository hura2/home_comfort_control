from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.sensor_reading_model import SensorReadingModel
    from models.sensor_type_model import SensorTypeModel


class SensorModel(Base):
    """
    センサー情報を格納するテーブルのモデル。
    センサーのコード、ラベル、設置場所、種類、カテゴリを管理します。
    """

    __tablename__ = "sensors"

    # 自動増加する数値型の主キー
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""

    # センサーの一意な識別コード (例: "floor", "ceiling")
    sensor_code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    """センサーの一意な識別コード"""

    # センサーのラベル (例: "リビング", "書斎")
    label: Mapped[str] = mapped_column(Text, nullable=False)
    """ラベル"""

    # センサーの設置場所 (例: "床", "天井", "南庭")
    location: Mapped[str] = mapped_column(Text, nullable=False)
    """設置場所"""

    # センサーの種類 (sensor_types テーブルへの外部キー)
    sensor_type_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sensor_types.id"), nullable=False
    )
    """種類"""

    # センサーのカテゴリ (例: "main", "sub", "supplementaries", "outdoor")
    category: Mapped[str] = mapped_column(Text, nullable=False)
    """カテゴリ"""

    # レコード作成日時
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ), nullable=False
    )
    """作成日時"""
    # SensorType とのリレーションシップ
    sensor_type: Mapped["SensorTypeModel"] = relationship("SensorTypeModel", back_populates="sensors")  # type: ignore
    """種類"""
    sensor_readings: Mapped["SensorReadingModel"] = relationship("SensorReadingModel", back_populates="sensor")  # type: ignore
    """測定結果"""
    # ユニーク制約の追加 (sensor_code)
    __table_args__ = (UniqueConstraint("sensor_code", name="uq_sensor_code"),)
