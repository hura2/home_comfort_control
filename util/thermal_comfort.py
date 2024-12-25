from datetime import time

from pythermalcomfort.models import pmv_ppd
from pythermalcomfort.utilities import clo_dynamic, v_relative

from settings import thermal_preference
from shared.dataclass.comfort_factors import ComfortFactors
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.pmv_result import PMVResult
from util.time_helper import TimeHelper


class ThermalComfort:
    """熱伝達性能を計算するクラス。

    Attributes:
        thermal_settings (ThermalPropertiesSettings): 熱特性設定
    """

    @staticmethod
    def calculate_pmv(
        home_sensor: HomeSensor,
        outdoor_temperature: float,  # 最高気温（度） - 外気温度として使用される最高気温
        comfort_factors: ComfortFactors,  # 快適さの要因
        wind_speed: float = 0.08,  # 風速（m/s）、デフォルトは0.08 m/s - 換気や風による熱伝達を考慮
    ) -> PMVResult:  # PMV計算の結果を返す - PMV計算結果を保持するPMVResultオブジェクト
        """PMV（Predicted Mean Vote）を計算するメソッド。

        人間の熱的快適性を評価するために、室内環境の様々なパラメータ（温度、湿度、風速、衣服の熱抵抗など）を元にPMVとPPD（Predicted Percentage of Dissatisfied）を計算します。これらの指標は、室内の温熱環境がどれくらい快適であるかを示します。

        Args:
            home_sensor (HomeSensor): 温度、湿度、CO2レベルなどのセンサーデータを提供するオブジェクト。
            temperature (float): 外気の最高気温（度）。室外の温度として使用され、外気の影響を反映します。
            comfort_factors (ComfortFactors): 快適さの要因を表すオブジェクト。
            wind_speed (float): 風速（m/s）。室内空間での換気や空気の流れを考慮した補正値。デフォルトは0.15 m/s。

        Returns:
            PMVResult: PMV、PPD、衣服の熱抵抗、相対空気速度など、計算に基づく結果をまとめたオブジェクト。
        """
        # 天井の温度を取得（センサーがない場合は主センサーの温度を使用）
        ceiling_temperature = (
            home_sensor.sub.air_quality.temperature
            if home_sensor.sub
            else home_sensor.main.air_quality.temperature
        )

        # 床の温度を取得（主センサーから）
        floor_temperature = home_sensor.main.air_quality.temperature

        # 屋根の表面温度を計算（外気温度を元に計算）
        roof_surface_temp = ThermalComfort._calculate_roof_surface_temperature(outdoor_temperature)

        # 西側外壁の表面温度を計算（外気温度に基づく計算）
        west_wall_surface_temp = ThermalComfort._calculate_west_wall_temperature(
            outdoor_temperature
        )

        # 壁の内部表面温度を計算（西側外壁温度と床温度を元に計算）
        wall_surface_temp = ThermalComfort._calculate_wall_surface_temperature(
            west_wall_surface_temp,  # 西側外壁の温度
            floor_temperature,  # 床の温度
            thermal_preference.home_spec.wall_thermal_conductivity,  # 壁材の熱伝導率
            thermal_preference.home_spec.window_thermal_conductivity,  # 窓材の熱伝導率
            thermal_preference.home_spec.window_to_wall_ratio,  # 窓と壁の面積比率
            thermal_preference.home_spec.wall_surface_heat_transfer_resistance,  # 壁の表面熱伝達抵抗
        )

        # 天井の内部表面温度を計算（屋根表面温度と天井温度を元に計算）
        ceiling_surface_temp = ThermalComfort._calculate_interior_surface_temperature(
            roof_surface_temp,  # 屋根の表面温度
            ceiling_temperature,  # 天井の温度
            thermal_preference.home_spec.ceiling_thermal_conductivity,  # 天井材の熱伝導率
            thermal_preference.home_spec.ceiling_surface_heat_transfer_resistance,  # 天井の表面熱伝達抵抗
        )

        # 床の内部表面温度を計算（外気と床温度を加重平均し、床の熱特性に基づいて計算）
        floor_surface_temp = ThermalComfort._calculate_interior_surface_temperature(
            (floor_temperature + outdoor_temperature)
            * (
                1 - thermal_preference.home_spec.temp_diff_coefficient_under_floor
            ),  # 外気と床温度の加重平均
            floor_temperature,  # 床の温度
            thermal_preference.home_spec.floor_thermal_conductivity,  # 床材の熱伝導率
            thermal_preference.home_spec.floor_surface_heat_transfer_resistance,  # 床の表面熱伝達抵抗
        )

        # 壁、天井、床の表面温度から平均放射温度を計算
        mean_radiant_temp = (wall_surface_temp + ceiling_surface_temp + floor_surface_temp) / 3

        # ドライバルブ温度（室温）を取得
        dry_bulb_temp = home_sensor.average_indoor_temperature

        # 湿度を取得
        humidity = home_sensor.average_indoor_humidity

        # 相対空気速度を計算（風速とメタボリック消費量に基づいて補正）
        relative_air_speed = v_relative(v=wind_speed, met=comfort_factors.met)

        # 動的な衣服の熱抵抗を計算（活動量と衣服による熱抵抗の変化を考慮）
        dynamic_clothing_insulation = clo_dynamic(clo=comfort_factors.clo, met=comfort_factors.met)

        # PMVとPPDを計算
        results = pmv_ppd(
            tdb=dry_bulb_temp,  # ドライバルブ温度
            tr=mean_radiant_temp,  # 平均放射温度
            vr=relative_air_speed,  # 相対空気速度
            rh=humidity,  # 湿度
            met=comfort_factors.met,  # メタボリックエネルギー消費量
            clo=dynamic_clothing_insulation,  # 動的な衣服の熱抵抗
            limit_inputs=False,
            standard="ASHRAE",  # 計算基準（ASHRAE）
        )

        pmv_result = PMVResult(
            pmv=float(results["pmv"]),  # PMV値（予測平均投票）
            ppd=float(results["ppd"]),  # PPD値（不快感を示す指標）
            clo=dynamic_clothing_insulation.item(0),  # 動的衣服熱抵抗（clo）
            air=relative_air_speed.item(0),  # 相対空気速度
            met=comfort_factors.met,  # メタボリックエネルギー消費量
            wall=wall_surface_temp,  # 壁の内部表面温度
            ceiling=ceiling_surface_temp,  # 天井の内部表面温度
            floor=floor_surface_temp,  # 床の内部表面温度
            mean_radiant_temperature=mean_radiant_temp,  # 平均放射温度
            dry_bulb_temperature=dry_bulb_temp,  # ドライバルブ温度
            relative_air_speed=relative_air_speed.item(0),  # 相対空気速度
            dynamic_clothing_insulation=dynamic_clothing_insulation.item(0),  # 動的衣服熱抵抗
        )

        # PMV計算結果をPMVResultオブジェクトとして返す
        return pmv_result

    @staticmethod
    def _calculate_interior_surface_temperature(
        outdoor_temperature: float,
        indoor_temperature: float,
        thermal_conductivity: float,
        surface_heat_transfer_resistance: float,
    ) -> float:
        """壁、天井、床の内部表面温度を計算するメソッド。

        Args:
            outdoor_temperature (float): 外気温（摂氏）
            indoor_temperature (float): 内気温（摂氏）
            thermal_conductivity (float): 材料の熱伝導率（W/(m·K)）
            surface_heat_transfer_resistance (float): 表面熱伝達抵抗（m²·K/W）

        Returns:
            float: 計算された内部表面温度（摂氏）
        """
        # 材料の熱抵抗を計算
        thermal_resistance = 1 / thermal_conductivity

        # 内部表面温度の計算
        interior_surface_temperature = indoor_temperature - (
            (surface_heat_transfer_resistance * (indoor_temperature - outdoor_temperature))
            / thermal_resistance
        )

        return interior_surface_temperature  # 計算された内部表面温度を返す

    @staticmethod
    def _calculate_wall_surface_temperature(
        outdoor_temperature: float,
        indoor_temperature: float,
        wall_thermal_conductivity: float,
        window_thermal_conductivity: float,
        window_to_wall_ratio: float,
        surface_heat_transfer_resistance: float,
    ) -> float:
        """壁の内部表面温度を計算するメソッド。

        Args:
            outdoor_temperature (float): 外気温（摂氏）
            indoor_temperature (float): 内気温（摂氏）
            wall_thermal_conductivity (float): 壁材の熱伝導率（W/(m·K)）
            window_thermal_conductivity (float): 窓材の熱伝導率（W/(m·K)）
            window_to_wall_ratio (float): 窓と壁の面積比率（0～1）
            surface_heat_transfer_resistance (float): 表面熱伝達抵抗（m²·K/W）

        Returns:
            float: 計算された壁の内部表面温度（摂氏）
        """
        # 複合熱伝導率を計算
        composite_thermal_conductivity = (
            window_to_wall_ratio * window_thermal_conductivity
            + (1 - window_to_wall_ratio) * wall_thermal_conductivity
        )

        # 内部表面温度の計算を呼び出す
        return ThermalComfort._calculate_interior_surface_temperature(
            outdoor_temperature,
            indoor_temperature,
            composite_thermal_conductivity,
            surface_heat_transfer_resistance,
        )

    @staticmethod
    def _calculate_west_wall_temperature(outdoor_temperature) -> float:
        """外気温と時間に基づき西側外壁の表面温度を計算する"""
        if not (time(13, 0) <= TimeHelper.get_current_time().time() < time(18, 0)):
            return outdoor_temperature

        if outdoor_temperature >= 40:
            return thermal_preference.wall_surface_temperatures.over_25
        elif outdoor_temperature >= 35:
            return thermal_preference.wall_surface_temperatures.over_30
        elif outdoor_temperature >= 30:
            return thermal_preference.wall_surface_temperatures.over_35
        elif outdoor_temperature >= 25:
            return thermal_preference.wall_surface_temperatures.over_40
        else:
            return outdoor_temperature

    @staticmethod
    def _calculate_roof_surface_temperature(outdoor_temperature) -> float:
        """外気温と時間に基づき屋根の表面温度を計算する"""
        if outdoor_temperature >= 40:
            return thermal_preference.roof_surface_temperatures.over_25
        elif outdoor_temperature >= 35:
            return thermal_preference.roof_surface_temperatures.over_35
        elif outdoor_temperature >= 30:
            return thermal_preference.roof_surface_temperatures.over_30
        elif outdoor_temperature >= 25:
            return thermal_preference.roof_surface_temperatures.over_40
        else:
            return outdoor_temperature
