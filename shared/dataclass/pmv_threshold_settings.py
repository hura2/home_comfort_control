from pydantic import BaseModel, Field
from shared.dataclass.aircon_settings import AirconSettings  # AirconSettingsがPydanticモデルであることを確認

class PMVThresholdSettings(BaseModel):
    """PMVに基づくエアコンの設定を保持するクラス"""

    threshold: float = Field(..., ge=-3, le=3, description="PMV閾値（-3〜+3）")
    """PMV閾値"""
    aircon_settings: AirconSettings = Field(..., description="エアコンの設定")
    """エアコンの設定"""