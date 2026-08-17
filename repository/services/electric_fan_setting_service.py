from datetime import datetime
from typing import Tuple

from sqlalchemy.orm import Session

from models.electric_fan_setting_model import ElectricFanSettingModel
from repository.queries.electric_fan_setting_queries import ElectricFanSettingQueries
from shared.dataclass.electric_fan_settings import ElectricFanSettings
from shared.enums.power_mode import PowerMode


class ElectricFanSettingService:
    """
    扇風機の設定を管理するビジネスロジッククラス。

    扇風機の設定の挿入や更新などのビジネスロジックを担当します。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session
        self.query = ElectricFanSettingQueries(session)

    def insert(
        self, measurement_id: int, electric_fan_settings: ElectricFanSettings
    ) -> ElectricFanSettingModel:
        """
        扇風機の設定を新しいデータベースに挿入します。

        Args:
            measurement_id (int): 測定データのID
            electric_fan_settings (ElectricFanSettings): 扇風機設定

        Returns:
            ElectricFanSettingModel: 挿入された扇風機の設定のインスタンス
        """
        return self.query.insert(
            measurement_id=measurement_id,
            fan_speed=electric_fan_settings.fan_speed,
            power=electric_fan_settings.power,
            swing=electric_fan_settings.swing,
            vertical_swing=electric_fan_settings.vertical_swing,
            rhythm=electric_fan_settings.rhythm,
        )

    def get_latest_electric_fan_settings(self) -> ElectricFanSettings:
        """
        最新の扇風機の設定情報を取得します。

        Returns:
            ElectricFanSettings: 最新の扇風機の設定情報
        """
        electric_fan_settings = self.query.get_latest_electric_fan_settings()
        if electric_fan_settings is None:
            return ElectricFanSettings()
        return ElectricFanSettings(
            power=PowerMode[electric_fan_settings.power],
            fan_speed=electric_fan_settings.fan_speed,
            swing=PowerMode[electric_fan_settings.swing],
            vertical_swing=PowerMode[electric_fan_settings.vertical_swing],
            rhythm=PowerMode[electric_fan_settings.rhythm],
        )

    def get_first_electric_fan_on_settings(
        self,
    ) -> Tuple[ElectricFanSettings | None, datetime | None]:
        """
        最初に電源がオンになった扇風機の設定情報を取得します。

        Returns:
            ElectricFanSettings: 最初に電源がオンになった扇風機の設定情報
        """
        electric_fan_setting_model = self.query.get_first_electric_fan_on_settings()
        if electric_fan_setting_model is None:
            return ElectricFanSettings(), None
        return (
            ElectricFanSettings(
                power=PowerMode[electric_fan_setting_model.power],
                fan_speed=electric_fan_setting_model.fan_speed,
                swing=PowerMode[electric_fan_setting_model.swing],
                vertical_swing=PowerMode[electric_fan_setting_model.vertical_swing],
                rhythm=PowerMode[electric_fan_setting_model.rhythm],
            ),
            electric_fan_setting_model.measurement.measurement_time,
        )
