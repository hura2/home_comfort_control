from pydantic import BaseModel

class CirculatorPreference(BaseModel):
    """サーキュレーター設定を管理するクラス"""

    use_circulator: bool
    """サーキュレーターを使用するかどうか"""

