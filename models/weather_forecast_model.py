from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.weather_forecast_hourly_model import WeatherForecastHourlyModel


class WeatherForecastModel(Base):
    """
    日単位の天気予報データを格納するモデル。
    """

    __tablename__ = "weather_forecast"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    forecast_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """予報日付"""
    max_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    """最高気温"""
    min_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    """最低気温"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(LOCAL_TZ)
    )
    """作成日時"""
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(LOCAL_TZ),
        onupdate=lambda: datetime.now(LOCAL_TZ),
        nullable=False,
    )
    """更新日時"""
    hourly_forecasts: Mapped[list["WeatherForecastHourlyModel"]] = relationship(
        "WeatherForecastHourlyModel",
        back_populates="weather_forecast",
        cascade="all, delete-orphan",
    )
    """日単位の天気予報データ"""
