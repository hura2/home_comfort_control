from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from util.env_config_loader import EnvConfigLoader


class DBSessionManager:
    """SQLAlchemyセッションの管理を行うクラス"""

    @staticmethod
    def create_url(environment: str | None = None) -> str:
        """データベース接続用のURLを作成するメソッド"""
        # 環境を指定しない場合は、デフォルトでローカルを使用
        if environment is None:
            environment = EnvConfigLoader.get_variable("ENVIRONMENT").lower()

        # 環境ごとに設定を切り替え
        if environment == "supabase":
            db_user = EnvConfigLoader.get_variable("SUPABASE_DB_USER")
            db_pass = EnvConfigLoader.get_variable("SUPABASE_DB_PASS")
            db_host = EnvConfigLoader.get_variable("SUPABASE_DB_HOST")
            db_name = EnvConfigLoader.get_variable("SUPABASE_DB_NAME")
            url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
        else:  # ローカル
            db_user = EnvConfigLoader.get_variable("LOCAL_DB_USER")
            db_pass = EnvConfigLoader.get_variable("LOCAL_DB_PASS")
            db_host = EnvConfigLoader.get_variable("LOCAL_DB_HOST")
            db_port = EnvConfigLoader.get_variable("LOCAL_DB_PORT")
            db_name = EnvConfigLoader.get_variable("LOCAL_DB_NAME")
            url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

        return url

    # エンジンの作成
    _engine = create_engine(create_url(), echo=False)

    # セッションの作成
    _session = sessionmaker(bind=_engine)

    @staticmethod
    def session():
        """セッションを取得するメソッド"""
        return DBSessionManager._session()

    @staticmethod
    @contextmanager
    def auto_commit_session():
        """セッションスコープを管理するコンテキストマネージャー"""
        session = DBSessionManager.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
