from pydantic import BaseModel, Field

class Co2ThresholdsPreference(BaseModel):
    """CO2閾値を管理するクラス"""

    high: int = Field(..., ge=500, le=2000)
    """高レベルの閾値 (g/m³), 一般的には高いCO2濃度の閾値"""

    warning: int = Field(..., ge=500, le=2000)
    """警告レベルの閾値 (g/m³), 警告として設定されるCO2濃度の閾値"""