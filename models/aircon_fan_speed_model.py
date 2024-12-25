from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models.aircon_setting_model import AirconSettingModel


class AirconFanSpeedModel(Base):
    """
    エアコンの送風量を定義するテーブル。
    - 主キーとして `name` を使用し、わかりやすく管理。
    - description に送風量の説明を保持可能。
    """

    __tablename__ = "aircon_fan_speeds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    """送風量の説明"""

    aircon_settings: Mapped["AirconSettingModel"] = relationship(
        "AirconSettingModel", back_populates="fan_speed"
    )
