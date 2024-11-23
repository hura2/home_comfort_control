import datetime
import time
from enum import Enum
from pathlib import Path

import yaml
from common.constants import SensorType
from models.sensor import Sensor


class GeneralSettings:
    """
    一般設定を管理するクラス。

    このクラスは設定ファイル（YAML形式）から一般的な設定値を読み込み、
    その値をプロパティとして取得できるように提供します。
    """

    class _Settings(Enum):
        """設定項目を定義する列挙型"""

        TIME_SETTINGS = "time_settings"  # 時刻設定
        ENVIRONMENT_SETTINGS = "environment_settings"  # 環境設定
        TEMPERATURE_THRESHOLDS = "temperature_thresholds"  # 温度閾値
        CO2_THRESHOLDS = "co2_thresholds"  # CO2閾値
        SENSORS = "sensors"  # センサー設定
        CIRCULATOR_SETTINGS = "circulator_settings"  # サーキュレーター設定
        DATABSE_SETTINGS = "database_settings"  # データベース設定
        SMART_DEVICE_SETTINGS = "smart_device_settings" # SmartDevice設定
        NOTIFY_SETTINGS = "notify_settings" # 通知設定

    def __init__(self):
        # 設定ファイルのパスを定義
        self.config_file = Path(__file__).parent.parent / "yaml" / "settings.yaml"
        # 設定をロード
        self.config = self._load_config()
        # 各設定を初期化
        self.time_settings = self._TimeSettings(self.config[self._Settings.TIME_SETTINGS.value])
        self.environment_settings = self._EnvironmentSettings(self.config[self._Settings.ENVIRONMENT_SETTINGS.value])
        self.temperature_thresholds = self._TemperatureThresholds(
            self.config[self._Settings.TEMPERATURE_THRESHOLDS.value]
        )
        self.co2_thresholds = self._Co2Thresholds(self.config[self._Settings.CO2_THRESHOLDS.value])
        self.sensors = self._Sensors(self.config[self._Settings.SENSORS.value])
        self.circulator_settings = self._CirculatorSettings(self.config[self._Settings.CIRCULATOR_SETTINGS.value])
        self.database_settings = self._DatabaseSettings(self.config[self._Settings.DATABSE_SETTINGS.value])
        self.smart_device_settings = self._SmartDeviceSettings(self.config[self._Settings.SMART_DEVICE_SETTINGS.value])
        self.notify_settings = self._NotifySettings(self.config[self._Settings.NOTIFY_SETTINGS.value])
    def _load_config(self):
        # YAMLファイルを読み込み、設定を返す
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    class _TimeSettings:
        """時刻設定を管理するクラス"""

        class _Settings(Enum):
            """設定項目を定義する列挙型"""

            AWAKE_PERIOD = "awake_period"

        def __init__(self, config):
            self.config = config
            # 覚醒期間を格納
            self.awake_period = self._AwakePeriod(self.config[self._Settings.AWAKE_PERIOD.value])

        class _AwakePeriod:
            """覚醒期間を管理するクラス"""

            class _Settings(Enum):
                START_TIME = "start_time"  # 覚醒期間の開始時間
                END_TIME = "end_time"  # 覚醒期間の終了時間

            def __init__(self, config):
                self.config = config

            @property
            def start_time(self) -> time:
                """ 
                覚醒期間の開始時間を取得する

                Returns:
                    time: 覚醒期間の開始時間
                """
                hour, minute = map(int, self.config[self._Settings.START_TIME.value].split(":"))
                return datetime.time(hour, minute)

            @property
            def end_time(self) -> time:
                """
                覚醒期間の終了時間を取得する

                Returns:
                    time: 覚醒期間の終了時間
                """
                hour, minute = map(int, self.config[self._Settings.END_TIME.value].split(":"))
                return datetime.time(hour, minute)

    class _EnvironmentSettings:
        """環境設定を管理するクラス"""

        class _Settings(Enum):
            DEHUMIDIFICATION_THRESHOLD = "dehumidification_threshold"  # 除湿運転しきい値
            PMV_THRESHOLD = "pmv_threshold"  # PMVしきい値

        def __init__(self, config):
            self.config = config

        @property
        def dehumidification_threshold(self) -> float:
            """
            除湿運転しきい値を取得する

            Returns:
                float: 除湿運転しきい値
            """
            return self.config[self._Settings.DEHUMIDIFICATION_THRESHOLD.value]

        @property
        def pmv_threshold(self) -> float:
            """
            PMVしきい値を取得する

            Returns:
                float: PMVしきい値
            """
            return self.config[self._Settings.PMV_THRESHOLD.value]

    class _TemperatureThresholds:
        """温度閾値を管理するクラス"""

        class _Settings(Enum):
            HIGH_TEMPERATURE = "high_temperature"  # 高温の閾値
            LOW_TEMPERATURE = "low_temperature"  # 低温の閾値

        def __init__(self, config):
            self.config = config

        @property
        def high_temperature_threshold(self) -> float:
            """
            高温の閾値を取得する

            Returns:
                float: 高温の閾値
            """
            return self.config[self._Settings.HIGH_TEMPERATURE.value]

        @property
        def low_temperature_threshold(self) -> float:
            """
            低温の閾値を取得する

            Returns:
                float: 低温の閾値
            """
            return self.config[self._Settings.LOW_TEMPERATURE.value]

    class _Co2Thresholds:
        """CO2閾値を管理するクラス"""

        class _Settings(Enum):
            HIGH_LEVEL_THRESHOLD = "high_level_threshold"  # 高レベルの閾値
            WARNING_LEVEL_THRESHOLD = "warning_level_threshold"  # 警告レベルの閾値

        def __init__(self, config):
            self.config = config

        @property
        def high_level_threshold(self) -> float:
            """
            高レベルの閾値を取得する            
            Returns:
                float: 高レベルの閾値"""
            return self.config[self._Settings.HIGH_LEVEL_THRESHOLD.value]

        @property
        def warning_level_threshold(self) -> float:
            """ 
            警告レベルの閾値を取得する

            Returns:
                float: 警告レベルの閾値
            """
            return self.config[self._Settings.WARNING_LEVEL_THRESHOLD.value]

    class _Sensors:
        """センサー設定を管理するクラス"""

        class _Settings(Enum):
            MAIN = "main" # 主センサ
            SUB = "sub" # 副センサ
            SUPPLEMENTARIES = "supplementaries" # 付属センサ
            OUTDOOR = "outdoor" # 屋外センサ

        def __init__(self, config):
            self.config = config
            # 主センサー情報を格納
            self.main = self._create_sensor(self._SensorData(config[self._Settings.MAIN.value]))
            # 副センサー情報を格納
            self.sub = (
                self._create_sensor(self._SensorData(config[self._Settings.SUB.value]))
                if self._Settings.SUB.value in config
                else None
            )
            # 付属センサー情報を格納
            self.supplementaries = [
                self._create_sensor(self._SensorData(s)) for s in config.get(self._Settings.SUPPLEMENTARIES.value, [])
            ]
            # 屋外センサー情報を格納
            self.outdoor = (
                self._create_sensor(self._SensorData(config[self._Settings.OUTDOOR.value]))
                if self._Settings.OUTDOOR.value in config
                else None
            )

        def _create_sensor(self, sensor_data: "_SensorData") -> Sensor:
            """
            センサー設定からSensorデータクラスのインスタンスを生成する。

            Args:
                sensor_config (dict): センサー設定の辞書

            Returns:
                Sensor: センサー情報を格納したデータクラス
            """
            return Sensor(
                id=sensor_data.id,
                label=sensor_data.label,
                location=sensor_data.location,
                type=SensorType.get_by_description(sensor_data.type),  # 例: SensorType.TEMPERATURE_HUMIDITY
            )

        class _SensorData:
            """センサーのデータを管理するクラス"""

            class _Settings(Enum):
                ID = "id"
                LABEL = "label"
                LOCATION = "location"
                TYPE = "type"

            def __init__(self, config):
                self.config = config

            @property
            def id(self) -> str:
                """
                センサーのIDを取得する
                """
                return self.config[self._Settings.ID.value]

            @property
            def label(self) -> str:
                """ 
                センサーのラベルを取得する
                """
                return self.config[self._Settings.LABEL.value]

            @property
            def location(self) -> str:
                """
                センサーの設置場所を取得する
                """
                return self.config[self._Settings.LOCATION.value]

            @property
            def type(self) -> str:
                return self.config[self._Settings.TYPE.value]

    class _CirculatorSettings:
        """circulator設定を管理するクラス"""

        class _Settings(Enum):
            USE_CIRCULATOR = "use_circulator" # サーキュレーターを使用するかどうか

        def __init__(self, config):
            self.config = config

        @property
        def use_circulator(self) -> bool:
            """ 
            サーキュレーターを使用するかどうかを取得する
            """
            return self.config[self._Settings.USE_CIRCULATOR.value]
    
    class _DatabaseSettings:
        """Database設定を管理するクラス"""

        class _Settings(Enum):
            USE_DATABASE = "use_database" # Databaseを使用するかどうか

        def __init__(self, config):
            self.config = config

        @property
        def use_database(self) -> bool:
            """  
            Databaseを使用するかどうかを取得する
            """
            return self.config[self._Settings.USE_DATABASE.value]
        
    class _SmartDeviceSettings:
        """SmartDevice設定を管理するクラス"""

        class _Settings(Enum):
            DEVICE_TYPE = "device_type" # SmartDeviceの種類

        def __init__(self, config):
            self.config = config

        @property
        def device_type(self) -> str:
            """  
            SmartDeviceの種類を取得する
            """
            return self.config[self._Settings.DEVICE_TYPE.value]
        
    class _NotifySettings:
        """Notify設定を管理するクラス"""

        class _Settings(Enum):
            ENABLE_LINE_NOTIFY = "enable_line_notify"
            ENABLE_DISCORD_NOTIFY = "enable_discord_notify"

        def __init__(self, config):
            self.config = config

        @property
        def enable_line_notify(self) -> bool:
            """  
            Line Notifyを使用するかどうかを取得する
            """
            return self.config[self._Settings.ENABLE_LINE_NOTIFY.value]
        
        @property
        def enable_discord_notify(self) -> bool:
            """  
            Discord Notifyを使用するかどうかを取得する
            """
            return self.config[self._Settings.ENABLE_DISCORD_NOTIFY.value]