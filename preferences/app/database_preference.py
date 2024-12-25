from pydantic import BaseModel


class Databaseference(BaseModel):
    """データベースの設定"""
    use_database: bool
    """使用するかどうか"""
