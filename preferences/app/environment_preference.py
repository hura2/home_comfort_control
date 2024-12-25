from pydantic import BaseModel, Field


class EnvironmentPreference(BaseModel):
    """環境設定"""
    
    dehumidification_threshold: float = Field(..., ge=0, le=30)
    """除湿運転しきい値 (g/m³), 一般的な範囲は0から30 g/m³"""

    pmv_threshold: float = Field(..., ge=-3, le=3)
    """PMVしきい値, 範囲は-3から+3"""
