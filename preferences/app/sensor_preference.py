from enum import Enum

from pydantic import BaseModel

from shared.dataclass.sensor import Sensor


class SensorsPreference(BaseModel):
    """センサー設定を管理するクラス"""

    main: Sensor
    """メインセンサー"""
    sub: Sensor
    """サブセンサー"""
    supplementaries: list[Sensor]
    """補助センサー"""
    outdoor: Sensor
    """屋外センサー"""
