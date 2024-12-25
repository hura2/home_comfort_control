from sqlalchemy.orm import Session

from models.sensor_type_model import SensorTypeModel  # AirconModeモデルをインポート


class SensorTypeQueries:
    """
    SensorType テーブルに関連するクエリを実行するクラス。
    - 主にモードの挿入や取得を提供。
    """

    def __init__(self, session: Session):
        """
        クラスの初期化。
        :param session: SQLAlchemyセッションオブジェクト。
        """
        self.session = session

    def get_type_by_name(self, name: str) -> SensorTypeModel | None:
        """
        名前でセンサタイプを取得する。
        :param name: センサタイプ名。
        :return: SensorType オブジェクトまたは None（見つからない場合）。
        """
        return self.session.query(SensorTypeModel).filter_by(name=name).first()
