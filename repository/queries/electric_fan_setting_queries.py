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

    def get_first_electric_fan_on_settings(
        self,
    ) -> ElectricFanSettingModel | None:
        """
        現在電源ONが継続している場合、
        その連続ON期間の最初の設定を取得する。

        例:
            id  power
            10  OFF
            11  ON   ← 取得するレコード
            12  ON
            13  ON
            14  ON   ← 最新

        現在の最新レコードがOFFの場合は、扇風機が現在OFFなのでNoneを返す。
        """

        # 最新の扇風機設定を取得する。
        # idは時系列順に増加するため、降順にして先頭のレコードが最新。
        latest = (
            self.session.query(ElectricFanSettingModel)
            .order_by(ElectricFanSettingModel.id.desc())
            .first()
        )

        # 設定が1件も存在しない場合、または最新の電源状態がOFFの場合は、
        # 現在ONが継続している状態ではないためNoneを返す。
        if latest is None or latest.power != PowerMode.ON.name:
            return None

        # 現在の連続ON期間が始まる直前にある「直近のOFF」を取得する。
        #
        # 最新レコードより前のレコードだけを対象にし、
        # powerがOFFのものをidの降順で検索することで、
        # 最新レコードから最も近いOFFを取得する。
        latest_off = (
            self.session.query(ElectricFanSettingModel)
            .filter(
                ElectricFanSettingModel.id < latest.id,
                ElectricFanSettingModel.power == PowerMode.OFF.name,
            )
            .order_by(ElectricFanSettingModel.id.desc())
            .first()
        )

        latest_off_id = latest_off.id if latest_off is not None else None

        # 現在の連続ON期間に含まれるONレコードを検索する。
        query = self.session.query(ElectricFanSettingModel).filter(
            ElectricFanSettingModel.power == PowerMode.ON.name,
            ElectricFanSettingModel.id <= latest.id,
        )

        # 直近のOFFが存在する場合は、
        # そのOFFより後のONだけを現在の連続ON期間として扱う。
        #
        # 例えば、
        #   10 ON
        #   11 ON
        #   12 OFF ← latest_off_id
        #   13 ON  ← 対象
        #   14 ON  ← 対象
        #
        # の場合、id > 12 のONだけが対象になる。
        if latest_off_id is not None:
            query = query.filter(ElectricFanSettingModel.id > latest_off_id)

        # 現在の連続ON期間の中で、最も古いONレコードを取得する。
        # idの昇順にすることで、最初にONになったレコードが取得できる。
        return query.order_by(ElectricFanSettingModel.id.asc()).first()
