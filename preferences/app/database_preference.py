from pydantic import BaseModel


class Databaseference(BaseModel):
    """データベースの設定"""

    enabled: bool
    """使用するかどうか"""
