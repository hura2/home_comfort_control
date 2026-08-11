from pydantic import BaseModel


class ElectricFanPreference(BaseModel):
    """扇風機設定を管理するクラス"""

    enabled: bool
    """扇風機を使用するかどうか"""
