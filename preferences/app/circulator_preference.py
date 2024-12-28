from pydantic import BaseModel


class CirculatorPreference(BaseModel):
    """サーキュレーター設定を管理するクラス"""

    enabled: bool
    """サーキュレーターを使用するかどうか"""
