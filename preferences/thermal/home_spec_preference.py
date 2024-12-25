from pydantic import BaseModel, Field


class HomeSpecPreference(BaseModel):
    """家のスペックを管理するクラス"""

    wall_thermal_conductivity: float = Field(..., ge=0, description="壁の熱伝導率（0以上の値）")
    """壁の熱伝導率"""

    ceiling_thermal_conductivity: float = Field(
        ..., ge=0, description="天井の熱伝導率（0以上の値）"
    )
    """天井の熱伝導率"""

    floor_thermal_conductivity: float = Field(..., ge=0, description="床の熱伝導率（0以上の値）")
    """床の熱伝導率"""

    window_thermal_conductivity: float = Field(..., ge=0, description="窓の熱伝導率（0以上の値）")
    """窓の熱伝導率"""

    window_to_wall_ratio: float = Field(
        ..., ge=0, le=1, description="窓の面積の壁に対する比率（0から1の範囲）"
    )
    """窓の面積の壁に対する比率（0から1の範囲）"""

    wall_surface_heat_transfer_resistance: float = Field(
        ..., ge=0, description="壁の表面熱伝達抵抗 [(m K)/W]（0以上の値）"
    )
    """壁の表面熱伝達抵抗 [(m K)/W]"""

    ceiling_surface_heat_transfer_resistance: float = Field(
        ..., ge=0, description="天井の表面熱伝達抵抗 [(m K)/W]（0以上の値）"
    )
    """天井の表面熱伝達抵抗 [(m K)/W]"""

    floor_surface_heat_transfer_resistance: float = Field(
        ..., ge=0, description="床の表面熱伝達抵抗 [(m K)/W]（0以上の値）"
    )
    """床の表面熱伝達抵抗 [(m K)/W]"""

    temp_diff_coefficient_under_floor: float = Field(
        ..., ge=0, description="床下の温度差係数（0以上の値）"
    )
    """床下の温度差係数"""
