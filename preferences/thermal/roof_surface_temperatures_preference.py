from pydantic import BaseModel, Field

class RoofSurfaceTemperaturePreference(BaseModel):
    """屋根表面温度を管理するクラス"""

    over_25: float = Field(..., ge=-50, le=100, description="外気温が25度以上の時の屋根表面温度（-50度から100度の範囲）")
    """外気温が25度以上の時の屋根表面温度"""
    
    over_30: float = Field(..., ge=-50, le=100, description="外気温が30度以上の時の屋根表面温度（-50度から100度の範囲）")
    """外気温が30度以上の時の屋根表面温度"""
    
    over_35: float = Field(..., ge=-50, le=100, description="外気温が35度以上の時の屋根表面温度（-50度から100度の範囲）")
    """外気温が35度以上の時の屋根表面温度"""
    
    over_40: float = Field(..., ge=-50, le=100, description="外気温が40度以上の時の屋根表面温度（-50度から100度の範囲）")
    """外気温が40度以上の時の屋根表面温度"""