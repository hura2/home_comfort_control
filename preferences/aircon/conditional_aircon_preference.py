from pydantic import BaseModel, Field

from shared.dataclass.aircon_settings import AirconSettings


class ConditionalAirconPreference(BaseModel):
    """
    環境制御設定（冷房・暖房の起動状態）を管理するクラス。
    冷房起動設定やOFF状態設定を含みます。
    """

    activation: "ActivationPreference" = Field(..., description="冷房起動設定")
    """冷房起動設定"""

    off_state: "OffStatePreference" = Field(..., description="OFF状態設定")
    """冷房をOFFにする設定"""


class ActivationPreference(BaseModel):
    """
    冷房起動の環境制御設定項目を管理するクラス。
    外気温との差異とPMV閾値を設定します。
    """

    outdoor_temperature_diff: float = Field(
        ..., ge=0.0, le=10.0, description="有効化基準の外気温との差"
    )
    """有効化基準の外気温との差（℃）"""

    threshold: float = Field(..., ge=-3.0, le=3.0, description="有効化基準のPMV")
    """有効化基準のPMV閾値"""


class OffStatePreference(BaseModel):
    """
    冷房OFF状態の環境制御設定項目を管理するクラス。
    """

    aircon_settings: AirconSettings
