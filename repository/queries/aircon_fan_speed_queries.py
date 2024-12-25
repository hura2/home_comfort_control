from sqlalchemy.orm import Session

from models.aircon_fan_speed_model import AirconFanSpeedModel  # AirconFanSpeedモデルをインポート


class AirconFanSpeedQueries:
    """
    AirconFanSpeed テーブルに関連するクエリを実行するクラス。
    - 送風量に関する挿入、取得、削除を提供。
    """

    def __init__(self, session: Session):
        """
        クラスの初期化。
        :param session: SQLAlchemyセッションオブジェクト。
        """
        self.session = session

    def get_fan_speed_by_name(self, name: str) -> AirconFanSpeedModel | None:
        """
        名前で送風量を取得する。
        :param name: 送風量名。
        :return: AirconFanSpeed オブジェクトまたは None（見つからない場合）。
        """
        return self.session.query(AirconFanSpeedModel).filter_by(name=name).first()
