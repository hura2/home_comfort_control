from sqlalchemy.orm import Session

from models.electric_fan_setting_model import ElectricFanSettingModel
from shared.enums.power_mode import PowerMode


class ElectricFanSettingQueries:
    """
    扇風機の設定を管理するクエリクラス。
    """

    def __init__(self, session: Session):
        """
        コンストラクタ
        """
        self.session = session

    def insert(
        self,
        measurement_id: int,
        fan_speed: int,
        power: PowerMode,
        swing: PowerMode,
        vertical_swing: PowerMode,
        rhythm: PowerMode,
    ) -> ElectricFanSettingModel:
        """
        扇風機の設定を挿入する。

        Args:
            measurement_id (int): 測定ID
            fan_speed (int): ファン速度
            power (PowerMode): モード
            swing (PowerMode): 扇風機のスイング
            vertical_swing (PowerMode): 垂直扇風機のスイング
            rhythm (PowerMode): リズム

        Returns:
            ElectricFanSettingModel: 新しく挿入された扇風機設定
        """
        new_electric_fan_setting = ElectricFanSettingModel(
            measurement_id=measurement_id,
            fan_speed=fan_speed,
            power=power.name,
            swing=swing.name,
            vertical_swing=vertical_swing.name,
            rhythm=rhythm.name,
        )
        self.session.add(new_electric_fan_setting)
        self.session.flush()
        return new_electric_fan_setting

    def get_latest_electric_fan_settings(self) -> ElectricFanSettingModel | None:
        """
        最新の扇風機設定を取得する。

        Returns:
            ElectricFanSettingModel | None: 最新の扇風機設定。なければNone。
        """
        return (
            self.session.query(ElectricFanSettingModel)
            .order_by(ElectricFanSettingModel.id.desc())
            .first()
        )
