from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings import LOCAL_TZ

if TYPE_CHECKING:
    from models.weather_forecast_model import WeatherForecastModel


class WeatherForecastHourlyModel(Base):
    """
    時間単位の天気予報データを格納するモデル。
    """

    __tablename__ = "weather_forecast_hourly"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    """ID"""
    weather_forecast_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("weather_forecast.id", ondelete="CASCADE"), nullable=False
    )
    """親テーブルのID"""
    forecast_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """予報時刻"""
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    """気温"""

    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    """湿度"""

    pressure: Mapped[float | None] = mapped_column(SmallInteger, nullable=True)
    """気圧"""

    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    """風速"""

    wind_direction: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    """風向"""

    precipitation_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    """降水確率"""

    weather: Mapped[str | None] = mapped_column(Text, nullable=True)
    """天気"""

    cloud_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    """曇り度"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(LOCAL_TZ),
        nullable=False,
    )
    """作成日時"""
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(LOCAL_TZ),
        onupdate=lambda: datetime.now(LOCAL_TZ),
        nullable=False,
    )
    """更新日時"""

    weather_forecast: Mapped["WeatherForecastModel"] = relationship(
        "WeatherForecastModel", back_populates="hourly_forecasts"
    )
    """親テーブル"""
