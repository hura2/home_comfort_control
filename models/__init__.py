# myapp/models/__init__.py

# Baseの統一
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # プロジェクト全体で共通のBaseを使用

from models.aircon_change_interval_model import AirconChangeIntervalModel
from models.aircon_fan_speed_model import AirconFanSpeedModel

# 個別モデルのインポート
from models.aircon_mode_model import AirconModeModel
from models.aircon_setting_model import AirconSettingModel
from models.circulator_setting_model import CirculatorSettingModel
from models.measurement_model import MeasurementModel
from models.pmv_model import PmvModel
from models.sensor_model import SensorModel
from models.sensor_reading_model import SensorReadingModel
from models.sensor_type_model import SensorTypeModel
from models.weather_forecast_model import WeatherForecastModel
from models.weather_forecast_hourly_model import WeatherForecastHourlyModel
from models.aircon_intensity_score_model import AirconIntensityScoreModel