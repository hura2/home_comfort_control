from pydantic import BaseModel, Field


class AutoOffCountermeasurePreference(BaseModel):
    """
    扇風機の8時間自動オフ対策設定を管理するクラス。

    扇風機の自動オフ対策を有効にするか、
    有効にした場合に何時間で一旦OFFにするかを保持します。
    """

    enabled: bool = Field(..., description="8時間自動オフ対策を有効にするか")
    """8時間自動オフ対策を有効にするか"""

    hours: float = Field(..., gt=0, le=8, description="一旦OFFにするまでの時間")
    """扇風機をONにしてから一旦OFFにするまでの時間（時間）"""