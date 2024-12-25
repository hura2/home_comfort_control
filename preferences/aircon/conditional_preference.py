from pydantic import BaseModel, Field

from preferences.aircon.conditional_aircon_preference import ConditionalAirconPreference
from shared.dataclass.aircon_settings import AirconSettings


class ConditionalPreference(BaseModel):
    """環境制御設定（冷房、暖房、空気循環、除湿）を管理するクラス"""

    cooling: "ConditionalAirconPreference" = Field(..., description="冷房起動設定")
    """冷房起動設定"""

    heating: "ConditionalAirconPreference" = Field(..., description="暖房起動設定")
    """暖房起動設定"""

    summer_condensation: "SummerCondensationPreference" = Field(..., description="除湿設定")
    """除湿設定"""

    circulator_threshold: float = Field(..., ge=0, le=5, description="空気循環閾値")
    """空気循環閾値（0〜100の範囲）"""


class SummerCondensationPreference(BaseModel):
    """露点制御のための設定項目を管理するクラス"""

    dew_point_margin: float = Field(..., ge=-5, le=5, description="露点制御しない場合の温度")
    """露点制御しない場合の温度（-40〜50℃）"""

    pmv_threshold: float = Field(..., ge=-3, le=3, description="冷房時のPMV閾値")
    """冷房時のPMV閾値（-3〜+3、1桁の小数）"""

    cooling_stop: "CoolingStopPreference" = Field(..., description="冷房停止時の設定")
    """冷房停止時の設定"""

    condensation_override: "CondensationOverridePreference" = Field(..., description="冷房時の設定")
    """冷房時の設定"""


class CoolingStopPreference(BaseModel):
    """冷房停止時の設定項目を管理するクラス"""
    aircon_settings: AirconSettings


class CondensationOverridePreference(BaseModel):
    """冷房時の設定項目を管理するクラス"""
    aircon_settings: AirconSettings



class AirconPreference(BaseModel):
    """冷房・暖房の設定項目を管理するクラス"""

    temperature_min: float = Field(..., ge=-40, le=50, description="最小温度")
    """最小温度（-40〜50℃）"""

    temperature_max: float = Field(..., ge=-40, le=50, description="最大温度")
    """最大温度（-40〜50℃）"""

    mode: str = Field(..., description="モード設定（冷房、暖房など）")
    """エアコンのモード（冷房、暖房など）"""
