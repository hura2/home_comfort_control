import math
from datetime import time

from pythermalcomfort.models import pmv_ppd
from pythermalcomfort.utilities import clo_dynamic, v_relative

from common.data_types import ComfortFactors, HomeSensor, PMVResults
from settings.thermal_properties_settings import ThermalPropertiesSettings
from util.time import TimeUtil


class ThermalComfortCalculator:
    """熱伝達性能を計算するクラス。"""

    @staticmethod
    def calculate_pmv(
        home_sensor: HomeSensor,
        forecast_max_temperature: float,  # 最高気温（度） - 外気温度として使用される最高気温
        comfort_factors: ComfortFactors,  # 快適さの要因
        wind_speed: float = 0.15,  # 風速（m/s）、デフォルトは0.15 m/s - 換気や風による熱伝達を考慮
    ) -> PMVResults:  # PMV計算の結果を返す - PMV計算結果を保持するPMVCalculationオブジェクト
        """PMV（Predicted Mean Vote）を計算するメソッド。

        人間の熱的快適性を評価するために、室内環境の様々なパラメータ（温度、湿度、風速、衣服の熱抵抗など）を元にPMVとPPD（Predicted Percentage of Dissatisfied）を計算します。これらの指標は、室内の温熱環境がどれくらい快適であるかを示します。

        Args:
            home_sensor (HomeSensor): 温度、湿度、CO2レベルなどのセンサーデータを提供するオブジェクト。
            forecast_max_temperature (float): 外気の最高気温（度）。室外の温度として使用され、外気の影響を反映します。
            comfort_factors (ComfortFactors): 快適さの要因を表すオブジェクト。
            wind_speed (float, optional): 風速（m/s）。室内空間での換気や空気の流れを考慮した補正値。デフォルトは0.15 m/s。

        Returns:
            PMVCalculation: PMV、PPD、衣服の熱抵抗、相対空気速度など、計算に基づく結果をまとめたオブジェクト。
        """
        # 熱特性設定をロードする
        thermal_settings = ThermalPropertiesSettings()

        # 天井の温度を取得（センサーがない場合は主センサーの温度を使用）
        ceiling_temperature = (
            home_sensor.sub.air_quality.temperature
            if home_sensor.sub.air_quality.temperature
            else home_sensor.main.air_quality.temperature
        )

        # 床の温度を取得（主センサーから）
        floor_temperature = home_sensor.main.air_quality.temperature

        # 外気の温度を取得（外部センサーがない場合は最高気温を使用）
        outdoor_temperature = (
            home_sensor.outdoor.air_quality.temperature
            if home_sensor.outdoor.air_quality.temperature
            else forecast_max_temperature
        )

        # 屋根の表面温度を計算（外気温度を元に計算）
        roof_surface_temp = ThermalComfortCalculator._calculate_roof_surface_temperature(outdoor_temperature)

        # 西側外壁の表面温度を計算（外気温度に基づく計算）
        west_wall_surface_temp = ThermalComfortCalculator._calculate_west_wall_temperature(outdoor_temperature)

        # 壁の内部表面温度を計算（西側外壁温度と床温度を元に計算）
        wall_surface_temp = ThermalComfortCalculator._calculate_wall_surface_temperature(
            west_wall_surface_temp,  # 西側外壁の温度
            floor_temperature,  # 床の温度
            thermal_settings.thermal_properties.wall_thermal_conductivity,  # 壁材の熱伝導率
            thermal_settings.thermal_properties.window_thermal_conductivity,  # 窓材の熱伝導率
            thermal_settings.thermal_properties.window_to_wall_ratio,  # 窓と壁の面積比率
            thermal_settings.thermal_properties.wall_surface_heat_transfer_resistance,  # 壁の表面熱伝達抵抗
        )

        # 天井の内部表面温度を計算（屋根表面温度と天井温度を元に計算）
        ceiling_surface_temp = ThermalComfortCalculator._calculate_interior_surface_temperature(
            roof_surface_temp,  # 屋根の表面温度
            ceiling_temperature,  # 天井の温度
            thermal_settings.thermal_properties.ceiling_thermal_conductivity,  # 天井材の熱伝導率
            thermal_settings.thermal_properties.ceiling_surface_heat_transfer_resistance,  # 天井の表面熱伝達抵抗
        )

        # 床の内部表面温度を計算（外気と床温度を加重平均し、床の熱特性に基づいて計算）
        floor_surface_temp = ThermalComfortCalculator._calculate_interior_surface_temperature(
            (floor_temperature + outdoor_temperature)
            * (1 - thermal_settings.thermal_properties.temp_diff_coefficient_under_floor),  # 外気と床温度の加重平均
            floor_temperature,  # 床の温度
            thermal_settings.thermal_properties.floor_thermal_conductivity,  # 床材の熱伝導率
            thermal_settings.thermal_properties.floor_surface_heat_transfer_resistance,  # 床の表面熱伝達抵抗
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
        dynamic_clothing_insulation = clo_dynamic(clo=comfort_factors.icl, met=comfort_factors.met)

        print("dry_bulb_temp", dry_bulb_temp)
        print("mean_radiant_temp", mean_radiant_temp)
        print("relative_air_speed", relative_air_speed)
        print("humidity", humidity)
        print("comfort_factors.met", comfort_factors.met)
        print("comfort_factors.icl", comfort_factors.icl)
        print("dynamic_clothing_insulation", dynamic_clothing_insulation)

        # PMVとPPDを計算
        results = pmv_ppd(
            tdb=dry_bulb_temp,  # ドライバルブ温度
            tr=mean_radiant_temp,  # 平均放射温度
            vr=relative_air_speed,  # 相対空気速度
            rh=humidity,  # 湿度
            met=comfort_factors.met,  # メタボリックエネルギー消費量
            clo=dynamic_clothing_insulation,  # 動的な衣服の熱抵抗
            standard="ISO",  # 計算基準（ISO規格）
        )

        print("results", results)
        
        # PMV計算結果をPMVCalculationオブジェクトとして返す
        return PMVResults(
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
            relative_air_speed=relative_air_speed,  # 相対空気速度
            dynamic_clothing_insulation=dynamic_clothing_insulation,  # 動的衣服熱抵抗
        )

    @staticmethod
    def calculate_absolute_humidity(temperature: float, relative_humidity: float) -> float:
        """絶対湿度を計算するメソッド。

        Args:
            temperature (float): 温度（摂氏）
            relative_humidity (float): 相対湿度（％）

        Returns:
            float: 計算された絶対湿度（g/m³）
        """
        # 摂氏からケルビンに変換
        temperature_kelvin = temperature + 273.15

        # 飽和水蒸気圧の計算（hPa）
        saturated_vapor_pressure = 6.1078 * 10 ** ((7.5 * temperature) / (temperature + 237.3))

        # 絶対湿度の計算（g/m³）
        absolute_humidity = (217 * (relative_humidity / 100) * saturated_vapor_pressure) / temperature_kelvin

        return absolute_humidity  # 絶対湿度を返す

    @staticmethod
    def calculate_dew_point(temperature_celsius: float, relative_humidity: float) -> float:
        """露点温度を計算するメソッド。

        Args:
            temperature_celsius (float): 温度（摂氏）
            relative_humidity (float): 相対湿度（％）

        Returns:
            float: 計算された露点温度（摂氏）
        """
        a = 17.27  # 定数
        b = 237.7  # 定数

        # αを計算
        alpha = ((a * temperature_celsius) / (b + temperature_celsius)) + math.log(relative_humidity / 100.0)

        # 露点温度の計算
        dew_point = math.ceil(((b * alpha) / (a - alpha)) * 10) / 10  # 小数点第一位まで切り上げ

        return dew_point  # 露点温度を返す

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
            (surface_heat_transfer_resistance * (indoor_temperature - outdoor_temperature)) / thermal_resistance
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
            window_to_wall_ratio * window_thermal_conductivity + (1 - window_to_wall_ratio) * wall_thermal_conductivity
        )

        # 内部表面温度の計算を呼び出す
        return ThermalComfortCalculator._calculate_interior_surface_temperature(
            outdoor_temperature, indoor_temperature, composite_thermal_conductivity, surface_heat_transfer_resistance
        )

    @staticmethod
    def _calculate_west_wall_temperature(outdoor_temperature) -> float:
        """外気温と時間に基づき西側外壁の表面温度を計算する"""
        if not (time(13, 0) <= TimeUtil.get_current_time().time() < time(18, 0)):
            return outdoor_temperature

        # 熱特性設定
        thermal_settings = ThermalPropertiesSettings()

        if outdoor_temperature >= 40:
            return thermal_settings.wall_surface_temperatures.over_25
        elif outdoor_temperature >= 35:
            return thermal_settings.wall_surface_temperatures.over_30
        elif outdoor_temperature >= 30:
            return thermal_settings.wall_surface_temperatures.over_35
        elif outdoor_temperature >= 25:
            return thermal_settings.wall_surface_temperatures.over_40
        else:
            return outdoor_temperature

    @staticmethod
    def _calculate_roof_surface_temperature(outdoor_temperature) -> float:
        """外気温と時間に基づき屋根の表面温度を計算する"""
        # 熱特性設定
        thermal_settings = ThermalPropertiesSettings()

        if outdoor_temperature >= 40:
            return thermal_settings.roof_surface_temperatures.over_25
        elif outdoor_temperature >= 35:
            return thermal_settings.roof_surface_temperatures.over_35
        elif outdoor_temperature >= 30:
            return thermal_settings.roof_surface_temperatures.over_30
        elif outdoor_temperature >= 25:
            return thermal_settings.roof_surface_temperatures.over_40
        else:
            return outdoor_temperature
