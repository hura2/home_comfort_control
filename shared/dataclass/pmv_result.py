from pydantic import BaseModel, Field


class PMVResult(BaseModel):
    """
    PMV（Predicted Mean Vote）計算結果を表すPydanticモデル。

    Attributes:
        pmv (float): PMV値（快適度指数）。
        ppd (float): PPD値（不快指数）。
        clo (float): 衣服の断熱性。
        air (float): 空気の速度。
        met (float): MET値（代謝当量）。
        wall (float): 壁表面温度。
        ceiling (float): 天井表面温度。
        floor (float): 床表面温度。
        mean_radiant_temperature (float): 平均放射温度。
        dry_bulb_temperature (float): 乾球温度。
        relative_air_speed (float): 相対風速。
        dynamic_clothing_insulation (float): 動的な衣服の断熱性。
    """

    pmv: float = Field(..., description="PMV値（快適度指数）")
    """PMV値（快適度指数）"""
    ppd: float = Field(..., description="PPD値（不快指数）")
    """PPD値（不快指数）"""
    clo: float = Field(..., description="衣服の断熱性")
    """衣服の断熱性"""
    air: float = Field(..., description="空気の速度")
    """空気の速度"""
    met: float = Field(..., description="MET値（代謝当量）")
    """MET値（代謝当量）"""
    wall: float = Field(..., description="壁表面温度")
    """壁表面温度"""
    ceiling: float = Field(..., description="天井表面温度")
    """天井表面温度"""
    floor: float = Field(..., description="床表面温度")
    """床表面温度"""
    mean_radiant_temperature: float = Field(..., description="平均放射温度")
    """平均放射温度"""
    dry_bulb_temperature: float = Field(..., description="乾球温度")
    """乾球温度"""
    relative_air_speed: float = Field(..., description="相対風速")
    """相対風速"""
    dynamic_clothing_insulation: float = Field(..., description="動的な衣服の断熱性")
    """動的な衣服の断熱性"""
