from enum import Enum
from pathlib import Path

import yaml


class ThermalPropertiesSettings:
    """
    熱特性設定を管理するクラス。

    このクラスは設定ファイル（YAML形式）から熱特性に関連する設定値を読み込み、
    その値をプロパティとして取得できるように提供します。
    """

    class _Settings(Enum):
        """熱特性項目を定義する列挙型"""

        THERMAL_PROPERTIES = "thermal_properties"  # 熱特性設定
        ROOF_SURFACE_TEMPERATURES = "roof_surface_temperatures"  # 屋根表面温度
        WALL_SURFACE_TEMPERATURES = "wall_surface_temperatures"  # 壁表面温度

    def __init__(self):
        # 設定ファイルのパスを定義
        self.config_file = Path(__file__).parent.parent / "yaml" / "thermal_properties_settings.yaml"
        # 設定をロード
        self.config = self._load_config()
        # 熱特性を初期化
        self.thermal_properties = self._ThermalProperties(self.config[self._Settings.THERMAL_PROPERTIES.value])
        # 屋根表面温度と壁表面温度を初期化
        self.roof_surface_temperatures = self._RoofSurfaceTemperatures(
            self.config[self._Settings.ROOF_SURFACE_TEMPERATURES.value]
        )
        # 屋根表面温度と壁表面温度を初期化
        self.wall_surface_temperatures = self._WallSurfaceTemperatures(
            self.config[self._Settings.WALL_SURFACE_TEMPERATURES.value]
        )

    def _load_config(self):
        # YAMLファイルを読み込み、設定を返す
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    class _ThermalProperties:
        """熱特性を管理するクラス"""

        class _Settings(Enum):
            WALL_THERMAL_CONDUCTIVITY = "wall_thermal_conductivity"  # 壁の熱伝導率
            CEILING_THERMAL_CONDUCTIVITY = "ceiling_thermal_conductivity"  # 天井の熱伝導率
            FLOOR_THERMAL_CONDUCTIVITY = "floor_thermal_conductivity"  # 床の熱伝導率
            WINDOW_THERMAL_CONDUCTIVITY = "window_thermal_conductivity"  # 窓の熱伝導率
            WINDOW_TO_WALL_RATIO = "window_to_wall_ratio"  # 窓の面積の壁に対する比率
            WALL_SURFACE_HEAT_TRANSFER_RESISTANCE = (
                "wall_surface_heat_transfer_resistance"  # 壁の表面熱伝達抵抗 [(m K)/W]
            )
            CEILING_SURFACE_HEAT_TRANSFER_RESISTANCE = (
                "ceiling_surface_heat_transfer_resistance"  # 天井の表面熱伝達抵抗 [(m K)/W]
            )
            FLOOR_SURFACE_HEAT_TRANSFER_RESISTANCE = (
                "floor_surface_heat_transfer_resistance"  # 床の表面熱伝達抵抗 [(m K)/W]
            )
            TEMP_DIFF_COEFFICIENT_UNDER_FLOOR = "temp_diff_coefficient_under_floor"  # 床下の温度差係数

        def __init__(self, config):
            self.config = config

        @property
        def wall_thermal_conductivity(self) -> float:
            """壁の熱伝導率を取得"""
            return self.config[self._Settings.WALL_THERMAL_CONDUCTIVITY.value]

        @property
        def ceiling_thermal_conductivity(self) -> float:
            """天井の熱伝導率を取得"""
            return self.config[self._Settings.CEILING_THERMAL_CONDUCTIVITY.value]

        @property
        def floor_thermal_conductivity(self) -> float:
            """床の熱伝導率を取得"""
            return self.config[self._Settings.FLOOR_THERMAL_CONDUCTIVITY.value]

        @property
        def window_thermal_conductivity(self) -> float:
            """窓の熱伝導率を取得"""
            return self.config[self._Settings.WINDOW_THERMAL_CONDUCTIVITY.value]

        @property
        def window_to_wall_ratio(self) -> float:
            """窓の面積の壁に対する比率を取得"""
            return self.config[self._Settings.WINDOW_TO_WALL_RATIO.value]

        @property
        def wall_surface_heat_transfer_resistance(self) -> float:
            """壁の表面熱伝達抵抗を取得"""
            return self.config[self._Settings.WALL_SURFACE_HEAT_TRANSFER_RESISTANCE.value]

        @property
        def ceiling_surface_heat_transfer_resistance(self) -> float:
            """天井の表面熱伝達抵抗を取得"""
            return self.config[self._Settings.CEILING_SURFACE_HEAT_TRANSFER_RESISTANCE.value]

        @property
        def floor_surface_heat_transfer_resistance(self) -> float:
            """床の表面熱伝達抵抗を取得"""
            return self.config[self._Settings.FLOOR_SURFACE_HEAT_TRANSFER_RESISTANCE.value]

        @property
        def temp_diff_coefficient_under_floor(self) -> float:
            """床下の温度差係数を取得"""
            return self.config[self._Settings.TEMP_DIFF_COEFFICIENT_UNDER_FLOOR.value]

    class _RoofSurfaceTemperatures:
        """屋根表面温度を定義する列挙型"""

        class _Settings(Enum):
            OVER_25 = "over_25"  # 外気温が25度以上
            OVER_30 = "over_30"  # 外気温が30度以上
            OVER_35 = "over_35"  # 外気温が35度以上
            OVER_40 = "over_40"  # 外気温が40度以上

        def __init__(self, config):
            self.config = config

        @property
        def over_25(self) -> float:
            """外気温が25度以上の時の屋根表面温度を取得"""
            return self.config[self._Settings.OVER_25.value]

        @property
        def over_30(self) -> float:
            """外気温が30度以上の時の屋根表面温度を取得"""
            return self.config[self._Settings.OVER_30.value]

        @property
        def over_35(self) -> float:
            """外気温が35度以上の時の屋根表面温度を取得"""
            return self.config[self._Settings.OVER_35.value]

        @property
        def over_40(self) -> float:
            """外気温が40度以上の時の屋根表面温度を取得"""
            return self.config[self._Settings.OVER_40.value]

    class _WallSurfaceTemperatures:
        """西側外壁表面温度を定義する列挙型"""

        class _Settings(Enum):
            OVER_25 = "over_25"  # 外気温が25度以上
            OVER_30 = "over_30"  # 外気温が30度以上
            OVER_35 = "over_35"  # 外気温が35度以上
            OVER_40 = "over_40"  # 外気温が40度以上

        def __init__(self, config):
            self.config = config

        @property
        def over_25(self) -> float:
            """外気温が25度以上の時の西側外壁表面温度を取得"""
            return self.config[self._Settings.OVER_25.value]

        @property
        def over_30(self) -> float:
            """外気温が30度以上の時の西側外壁表面温度を取得"""
            return self.config[self._Settings.OVER_30.value]

        @property
        def over_35(self) -> float:
            """外気温が35度以上の時の西側外壁表面温度を取得"""
            return self.config[self._Settings.OVER_35.value]

        @property
        def over_40(self) -> float:
            """外気温が40度以上の時の西側外壁表面温度を取得"""
            return self.config[self._Settings.OVER_40.value]


# 使用例
# if __name__ == "__main__":
#     settings = ThermalPropertiesSettings()
#     print("壁の熱伝導率:", settings.wall_thermal_conductivity)
#     print("天井の熱伝導率:", settings.ceiling_thermal_conductivity)
#     print("床の熱伝導率:", settings.floor_thermal_conductivity)
#     print("窓の熱伝導率:", settings.window_thermal_conductivity)
#     print("窓の面積の壁に対する比率:", settings.window_to_wall_ratio)
#     print("壁の表面熱伝達抵抗:", settings.wall_surface_heat_transfer_resistance)
#     print("天井の表面熱伝達抵抗:", settings.ceiling_surface_heat_transfer_resistance)
#     print("床の表面熱伝達抵抗:", settings.floor_surface_heat_transfer_resistance)
#     print("床下の温度差係数:", settings.temp_diff_coefficient_under_floor)

#     print("屋根表面温度（25度以上）:", settings.roof_surface_temperature_over_25)
#     print("屋根表面温度（30度以上）:", settings.roof_surface_temperature_over_30)
#     print("屋根表面温度（35度以上）:", settings.roof_surface_temperature_over_35)
#     print("屋根表面温度（40度以上）:", settings.roof_surface_temperature_over_40)

#     print("西側外壁表面温度（25度以上）:", settings.wall_surface_temperature_over_25)
#     print("西側外壁表面温度（30度以上）:", settings.wall_surface_temperature_over_30)
#     print("西側外壁表面温度（35度以上）:", settings.wall_surface_temperature_over_35)
#     print("西側外壁表面温度（40度以上）:", settings.wall_surface_temperature_over_40)
