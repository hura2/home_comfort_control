from typing import List

from pydantic import BaseModel, Field

from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.pmv_threshold_settings import PMVThresholdSettings


class AirconSettingsPreference(BaseModel):
    """
    エアコン設定に関するPMV閾値やその他の設定を管理するクラス。

    設定値は外部の設定ファイルからロードされ、Pydanticモデルでバリデーションされます。
    """

    pmv_thresholds: List[PMVThresholdSettings]
    """PMV閾値に基づくエアコンの設定閾値を格納するリスト。"""

    dry: "BaseAirconSettingsPreference"
    """ドライ運転の設定。"""

    weakest_cooling: "BaseAirconSettingsPreference"
    """冷房の最弱設定。"""

    weakest_heating: "BaseAirconSettingsPreference"
    """暖房の最弱設定。"""

    class BaseAirconSettingsPreference(BaseModel):
        aircon_settings: AirconSettings
        """エアコン設定"""
