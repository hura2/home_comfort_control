from pydantic import BaseModel, Field

from preferences.circulator.thresholds_preference import ThresholdsPreference


class CirculatorPreference(BaseModel):
    """
    サーキュレーター設定を管理するクラス。

    このクラスはサーキュレーターに関連する設定値を保持し、
    各種温度設定をプロパティとして提供します。
    """

    thresholds: ThresholdsPreference = Field(
        ..., description="温度設定"
    )
    """温度設定"""