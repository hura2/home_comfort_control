from sqlalchemy.orm import Session

from models.aircon_mode_model import AirconModeModel  # AirconModeモデルをインポート


class AirconModeQueries:
    """
    AirconMode テーブルに関連するクエリを実行するクラス。
    - 主にモードの挿入や取得を提供。
    """

    def __init__(self, session: Session):
        """
        クラスの初期化。
        :param session: SQLAlchemyセッションオブジェクト。
        """
        self.session = session

    def get_mode_by_name(self, name: str) -> AirconModeModel | None:
        """
        名前でモードを取得する。
        :param name: モード名。
        :return: AirconMode オブジェクトまたは None（見つからない場合）。
        """
        return self.session.query(AirconModeModel).filter_by(name=name).first()
