from pydantic import BaseModel

from preferences.app.awake_period_preference import AwakePeriodPreference
from preferences.app.circulator_preference import CirculatorPreference
from preferences.app.co2_thresholds_preference import Co2ThresholdsPreference
from preferences.app.database_preference import Databaseference
from preferences.app.environment_preference import EnvironmentPreference
from preferences.app.notify_preference import NotifyPreference
from preferences.app.sensor_preference import SensorsPreference
from preferences.app.smart_home_device_preference import SmartHomeDevicePreference
from preferences.app.temperature_thresholds_preference import TemperatureThresholdsPreference
from preferences.app.weather_forecast_preference import WeatherForecastPreference


class AppPreference(BaseModel):
    """
    アプリの設定を管理するクラス
    """

    awake_period: AwakePeriodPreference
    """起床時刻"""
    environment: EnvironmentPreference
    """環境"""
    temperature_thresholds: TemperatureThresholdsPreference
    """温度防熱"""
    co2_thresholds: Co2ThresholdsPreference
    """CO2"""
    sensors: SensorsPreference
    """センサー"""
    circulator: CirculatorPreference
    """冷暖房"""
    database: Databaseference
    """データベース"""
    smart_home_device: SmartHomeDevicePreference
    """スマートホーム設備"""
    weather_forecast: WeatherForecastPreference
    """天気予報"""
    notify: NotifyPreference  # 複数の通知設定がある場合
