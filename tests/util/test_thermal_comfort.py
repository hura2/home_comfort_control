# test_thermal_comfort_calculator.py
import math
from unittest.mock import MagicMock, Mock

import pytest

from models.comfort_factors import ComfortFactors
from models.home_sensor import HomeSensor
from models.pmv_results import PMVResults
from models.sensor import Sensor
from settings.thermal_properties_settings import ThermalPropertiesSettings
from util.thermal_comfort import ThermalComfort


@pytest.fixture
def mock_comfort_factors():
    """Mock ComfortFactorsオブジェクトを作成するためのfixture"""
    return ComfortFactors(met=1.2, icl=0.5)


@pytest.fixture
def thermal_properties_settings():
    """ThermalPropertiesSettingsのモックオブジェクトを返すfixture"""
    # ThermalPropertiesSettingsのモックインスタンスを作成
    mock_settings = Mock(spec=ThermalPropertiesSettings)

    # thermal_propertiesオブジェクトとその属性にモック値を設定
    mock_settings.thermal_properties = Mock()
    mock_settings.thermal_properties.wall_thermal_conductivity = 0.8
    mock_settings.thermal_properties.window_thermal_conductivity = 1.2
    mock_settings.thermal_properties.window_to_wall_ratio = 0.4
    mock_settings.thermal_properties.wall_surface_heat_transfer_resistance = 0.25
    mock_settings.thermal_properties.ceiling_thermal_conductivity = 0.6
    mock_settings.thermal_properties.floor_thermal_conductivity = 0.9
    mock_settings.thermal_properties.temp_diff_coefficient_under_floor = 0.2

    return mock_settings


def test_calculate_pmv(mock_comfort_factors, thermal_properties_settings):
    """PMV計算のテスト"""

    # mainとsubをモック
    sub = MagicMock(spec=Sensor)
    main = MagicMock(spec=Sensor)
    outdoor = MagicMock(spec=Sensor)

    # subとmainに適切なモックデータを設定
    sub.air_quality.temperature = 25.0  # subの温度は25.0
    sub.air_quality.humidity = 50  # subの湿度は50
    main.air_quality.temperature = 25.0  # mainの温度は25.0
    main.air_quality.humidity = 50  # mainの湿度は50
    outdoor.air_quality.temperature = 30.0  # mainの温度は25.0
    outdoor.air_quality.humidity = 40

    home_sensor = HomeSensor(main=main, sub=sub, outdoor=outdoor)

    result = ThermalComfort.calculate_pmv(
        home_sensor=home_sensor,
        forecast_max_temperature=32.0,
        comfort_factors=mock_comfort_factors,
        wind_speed=0.1,
    )
    assert isinstance(result, PMVResults)
    assert -3 <= result.pmv <= 3
    assert 0 <= result.ppd <= 100
    assert result.mean_radiant_temperature > 0
    assert result.relative_air_speed > 0


# def test_calculate_absolute_humidity():
#     """絶対湿度計算のテスト"""
#     temperature = 25.0
#     relative_humidity = 60.0
#     absolute_humidity = ThermalComfort.calculate_absolute_humidity(temperature, relative_humidity)
#     assert math.isclose(absolute_humidity, 13.8, rel_tol=0.1)


# def test_calculate_dew_point():
#     """露点計算のテスト"""
#     temperature = 25.0
#     relative_humidity = 60.0
#     dew_point = ThermalComfort.calculate_dew_point(temperature, relative_humidity)
#     assert math.isclose(dew_point, 16.7, rel_tol=0.1)


def test_calculate_interior_surface_temperature():
    """内部表面温度計算のテスト"""
    outdoor_temperature = 30.0
    indoor_temperature = 25.0
    thermal_conductivity = 0.8
    surface_heat_transfer_resistance = 0.25

    surface_temp = ThermalComfort._calculate_interior_surface_temperature(
        outdoor_temperature,
        indoor_temperature,
        thermal_conductivity,
        surface_heat_transfer_resistance,
    )
    assert isinstance(surface_temp, float)
    assert 25.0 <= surface_temp <= 30.0
