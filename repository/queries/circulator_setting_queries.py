from sqlalchemy.orm import Session

from models.circulator_setting_model import CirculatorSettingModel
from shared.enums.power_mode import PowerMode


class CirculatorSettingQueries:
    """
    サーキュレーター設定を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(
        self, measurement_id: int, fan_speed: int, power: PowerMode
    ) -> CirculatorSettingModel:
        """
        サーキュレーター設定を挿入する。

        Args:
            measurement_id (int): 測定ID
            fan_speed (int): ファン速度
            power (PowerMode): モード

        Returns:
            CirculatorSettingModel: 新しく挿入されたサーキュレーター設定
        """
        new_circulator_setting = CirculatorSettingModel(
            measurement_id=measurement_id, fan_speed=fan_speed, power=power.name
        )
        self.session.add(new_circulator_setting)
        self.session.flush()
        return new_circulator_setting

    def get_latest_circulator_settings(self) -> CirculatorSettingModel | None:
        """
        最新のサーキュレーター設定を取得する。

        Returns:
            CirculatorSettingModel | None: 最新のサーキュレーター設定。なければNone。
        """
        return (
            self.session.query(CirculatorSettingModel)
            .order_by(CirculatorSettingModel.id.desc())
            .first()
        )
