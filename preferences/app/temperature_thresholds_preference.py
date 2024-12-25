from pydantic import BaseModel, Field


class TemperatureThresholdsPreference(BaseModel):
    """温度閾値を管理するクラス"""

    high: float = Field(..., ge=-100, le=100)
    """高温の閾値 (°C), 一般的な範囲は-100°Cから100°C"""

    low: float = Field(..., ge=-100, le=100)
    """低温の閾値 (°C), 一般的な範囲は-100°Cから100°C"""