from sqlalchemy.orm import Session

from models.circulator_setting_model import CirculatorSettingModel
from repository.queries.circulator_setting_queries import CirculatorSettingQueries
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.enums.power_mode import PowerMode


class CirculatorSettingService:
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
        self.query = CirculatorSettingQueries(session)

    def insert(
        self, measurement_id: int, circulator_settings: CirculatorSettings
    ) -> CirculatorSettingModel:
        """
        エアコン設定を新しいデータベースに挿入します。

        Args:
            measurement_id (int): 測定データのID
            circulator_settings (CirculatorSettings): エアコン設定

        Returns:
            CirculatorSettingModel: 挿入されたエアコン設定のインスタンス
        """
        return self.query.insert(
            measurement_id=measurement_id,
            fan_speed=circulator_settings.fan_speed,
            power=circulator_settings.power,
        )

    def get_latest_circulator_settings(self) -> CirculatorSettings:
        """
        最新のエアコン設定情報を取得します。

        Returns:
            CirculatorSettings: 最新のエアコン設定情報
        """
        circulator_settings = self.query.get_latest_circulator_settings()
        if circulator_settings is None:
            return CirculatorSettings(power=PowerMode.OFF, fan_speed=0)
        return CirculatorSettings(
            power=PowerMode[circulator_settings.power],
            fan_speed=circulator_settings.fan_speed,
        )
