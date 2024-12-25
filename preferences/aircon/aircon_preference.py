from pydantic import BaseModel, Field

from preferences.aircon.aircon_settings_preference import AirconSettingsPreference
from preferences.aircon.conditional_preference import ConditionalPreference


class AirconPreference(BaseModel):
    """
    エアコン設定を管理するクラス。

    このクラスは、エアコンの動作に関する各種設定を格納します。
    設定値は外部の設定ファイルからロードされ、Pydanticモデルでバリデーションされます。
    """

    aircon_settings: AirconSettingsPreference
    """エアコンのPMV閾値や動作モードに関連する設定を格納するフィールド。"""

    conditional: ConditionalPreference
    """環境制御に関する設定を格納するフィールド。"""
