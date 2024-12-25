from datetime import datetime
from typing import Tuple

from sqlalchemy.orm import Session

from models.aircon_setting_model import AirconSettingModel
from repository.queries.aircon_setting_queries import AirconSettingQueries
from shared.dataclass.aircon_settings import AirconSettings
from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from shared.enums.power_mode import PowerMode


class AirconSettingService:
    """
    エアコン設定を管理するビジネスロジッククラス。

    エアコン設定の挿入や更新などのビジネスロジックを担当します。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session
        self.query = AirconSettingQueries(session)

    def insert(self, measurement_id: int, aircon_settings: AirconSettings) -> AirconSettingModel:
        """
        エアコン設定を挿入します。

        Args:
            aircon_settings (AirconSettings): 挿入するエアコン設定情報

        Returns:
            AirconSettingsModel: 挿入されたエアコン設定情報
        """
        return self.query.insert(
            measurement_id=measurement_id,
            temperature=aircon_settings.temperature,
            mode=aircon_settings.mode,
            fan_speed=aircon_settings.fan_speed,
            power=aircon_settings.power,
        )

    def get_latest_aircon_settings(self) -> Tuple[AirconSettings | None, datetime | None]:
        """
        最新のエアコン設定情報を取得します。

        Returns:
            AirconSettings: 最新のエアコン設定情報
        """
        aircon_settings_model = self.query.get_latest_aircon_settings()
        if not aircon_settings_model:
            return None, None
        return (
            AirconSettings(
                temperature=aircon_settings_model.temperature,
                mode=AirconMode[aircon_settings_model.mode.name],
                fan_speed=AirconFanSpeed[aircon_settings_model.fan_speed.name],
                power=PowerMode[aircon_settings_model.power],
                force_fan_below_dew_point=False,
            ),
            aircon_settings_model.measurement.measurement_time,
        )

    def get_aircon_settings_by_date(self, date: str) -> list[AirconSettingModel]:
        """
        指定した日付のエアコン設定を取得するメソッド。

        :param date: 日付（例: "2024-12-25"）
        :return: エアコン設定のリスト
        """
        start_datetime = datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S")
        return self.query.get_aircon_settings_by_date(
            start_datetime.isoformat(), end_datetime.isoformat()
        )
