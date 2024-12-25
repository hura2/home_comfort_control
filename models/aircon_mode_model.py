from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models.aircon_change_interval_model import AirconChangeIntervalModel
    from models.aircon_setting_model import AirconSettingModel


class AirconModeModel(Base):
    """
    エアコンのモードを定義するテーブル。
    - 主キーとして `name` を使用し、わかりやすく管理。
    - description にモードの説明を保持可能。
    """

    __tablename__ = "aircon_modes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    """モード名"""

    aircon_change_intervals: Mapped["AirconChangeIntervalModel"] = relationship(
        "AirconChangeIntervalModel", back_populates="mode"
    )
    """モード別の変更間隔"""

    aircon_settings: Mapped["AirconSettingModel"] = relationship(
        "AirconSettingModel", back_populates="mode"
    )
    """モード別の設定"""
