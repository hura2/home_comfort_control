# ファイル名: thermal_preference.py

from pydantic import BaseModel

from preferences.thermal.home_spec_preference import HomeSpecPreference
from preferences.thermal.roof_surface_temperatures_preference import RoofSurfaceTemperaturePreference
from preferences.thermal.wall_surface_temperatures_preference import WallSurfaceTemperaturePreference



class ThermalPreference(BaseModel):
    """
    熱特性設定を管理するクラス。

    このクラスは設定ファイル（YAML形式）から熱特性に関連する設定値を読み込み、
    その値をプロパティとして取得できるように提供します。
    """

    home_spec: HomeSpecPreference
    """家のスペック設定"""

    roof_surface_temperatures: RoofSurfaceTemperaturePreference
    """屋根表面温度設定"""

    wall_surface_temperatures: WallSurfaceTemperaturePreference
    """壁表面温度設定"""