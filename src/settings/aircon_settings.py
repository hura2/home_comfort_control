from enum import Enum
from pathlib import Path
from typing import List

import yaml
from common import constants
from common.data_types import AirconState, PMVThresholdState


class _BaseAirconSettings:
    """エアコン設定の基底クラス"""

    class _Settings(Enum):
        """設定項目を定義する列挙型"""

        TEMPERATURE = "temperature"  # 温度
        MODE = "mode"  # モード
        FAN_SPEED = "fan_speed"  # 風速
        POWER = "power"

    def __init__(self, config):
        self.config = config

    def create_aircon_state(self, data: dict) -> AirconState:
        """dictからAirconStateを生成"""

        # AirconStateのデフォルトインスタンスを作成
        default_state = AirconState()
        return AirconState(
            temperature=data.get(self._Settings.TEMPERATURE.value, default_state.temperature),
            mode=constants.AirconMode[data.get(self._Settings.MODE.value, default_state.mode.name)],
            fan_speed=constants.AirconFanSpeed[data.get(self._Settings.FAN_SPEED.value, default_state.fan_speed.name)],
            power=constants.AirconPower[data.get(self._Settings.POWER.value, default_state.power.name)],
        )

    @property
    def aircon_state(self) -> AirconState:
        """設定から単一のAirconStateを取得"""
        return self.create_aircon_state(self.config)


class AirconSettings:
    """
    エアコン設定を管理するクラス。

    このクラスは設定ファイル（YAML形式）からエアコンに関連する設定値を読み込み、
    その値をプロパティとして取得できるように提供します。
    """

    class _Settings(Enum):
        """エアコン設定項目を定義する列挙型"""

        PMV_THRESHOLD_SETTINGS = "pmv_threshold_settings"  # PMV閾値設定
        ENVIRONMENTAL_CONTROL_SETTINGS = "environmental_control_settings"  # 環境設定
        WEAKEST_AIRCON_SETTINGS = "weakest_aircon_settings"

    def __init__(self):
        # 設定ファイルのパスを定義
        self.config_file = Path(__file__).parent.parent / "yaml" / "aircon_settings.yaml"
        # 設定をロード
        self.config = self._load_config()
        # サブクラスを初期化
        self.pmv_threshold_settings = self._PMVThresholdSettings(
            self.config[self._Settings.PMV_THRESHOLD_SETTINGS.value]
        )
        # サブクラスを初期化
        self.environmental_control_settings = self._EnvironmentalControlSettings(
            self.config[self._Settings.ENVIRONMENTAL_CONTROL_SETTINGS.value]
        )
        # サブクラスを初期化
        self.weakest_aircon_settings = self._WeakestAirconSettings(
            self.config[self._Settings.WEAKEST_AIRCON_SETTINGS.value]
        )

    def _load_config(self):
        """YAMLファイルを読み込み、設定を返す"""
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    class _PMVThresholdSettings(_BaseAirconSettings):
        """PMV閾値設定項目を定義する列挙型"""

        class _PMVSettings(Enum):
            """PMV閾値設定項目を定義する列挙型"""

            PMV_THRESHOLDS = "pmv_thresholds"  # PMV閾値

        class _PMVThresholds(Enum):
            """PMV閾値設定項目を定義する列挙型"""

            THRESHOLD = "threshold"  # 閾値

        def __init__(self, config):
            self.config = config

        @property
        def pmv_thresholds(self) -> List[PMVThresholdState]:
            """PMVに基づくエアコンの設定閾値を取得"""
            thresholds = self.config[self._PMVSettings.PMV_THRESHOLDS.value]
            pmv_threshold_settings = []
            for threshold in thresholds:
                # print(threshold)
                aircon_state = self.create_aircon_state(threshold)
                pmv_threshold_settings.append(
                    PMVThresholdState(
                        threshold=threshold.get(self._PMVThresholds.THRESHOLD.value), aircon_state=aircon_state
                    )
                )

            return pmv_threshold_settings

    class _EnvironmentalControlSettings:
        """環境制御設定項目を定義する列挙型"""

        class _Settings(Enum):
            """環境制御設定項目を定義する列挙型"""

            COOLING_ACTIVATION_CRITERIA = "cooling_activation_criteria"  # 冷房起動設定
            HEATING_ACTIVATION_CRITERIA = "heating_activation_criteria"  # 暖房起動設定
            AIR_CIRCULATION_THRESHOLD = "air_circulation_threshold"  # 空気循環閾値
            DEHUMIDIFICATION_SETTINGS = "dehumidification_settings"  # 除湿設定
            DEW_POINT_CONTROL = "dew_point_control"  # 露点制御

        def __init__(self, config):
            self.config = config
            # 冷房起動設定を初期化
            self.cooling_activation_criteria = self._ActivationCriteria(
                self.config[self._Settings.COOLING_ACTIVATION_CRITERIA.value]
            )
            # 暖房起動設定を初期化
            self.heating_activation_criteria = self._ActivationCriteria(
                self.config[self._Settings.HEATING_ACTIVATION_CRITERIA.value]
            )
            # 除湿設定を初期化
            self.dehumidification_settings = self._DehumidificationSettings(
                self.config[self._Settings.DEHUMIDIFICATION_SETTINGS.value]
            )
            # 空気循環閾値を初期化
            self.air_circulation_threshold = self.config[self._Settings.AIR_CIRCULATION_THRESHOLD.value]
            # 露点制御を初期化
            self.dew_point_control = self._DewPointControl(self.config[self._Settings.DEW_POINT_CONTROL.value])

        class _ActivationCriteria(_BaseAirconSettings):
            """有効化基準設定項目を定義する列挙型"""

            class _ActivationCriteriaSettings(Enum):
                """有効化基準項目を定義する列挙型"""

                OUTDOOR_TEMPERATURE_DIFFERENCE = "outdoor_temperature_difference"  # 外気温との差
                PMV_THRESHOLD = "pmv_threshold"  # PMV閾値

            @property
            def outdoor_temperature_difference(self) -> float:
                """有効化基準の外気温との差を取得"""
                return self.config[self._ActivationCriteriaSettings.OUTDOOR_TEMPERATURE_DIFFERENCE.value]

            @property
            def pmv_threshold(self) -> float:
                """有効化基準のPMV閾値を取得"""
                return self.config[self._ActivationCriteriaSettings.PMV_THRESHOLD.value]

        class _DehumidificationSettings(_BaseAirconSettings):
            """除湿設定項目を定義する列挙型"""

        class _DewPointControl:
            """露点制御設定項目を定義する列挙型"""

            class _Settings(Enum):
                """露点制御設定項目を定義する列挙型"""

                CONDENSATION_PREVENTION_THRESHOLD = "condensation_prevention_threshold"  # 露点制御しない場合の温度
                PMV_THRESHOLD_FOR_COOLING = "pmv_threshold_for_cooling"  # 冷房時のPMV閾値
                COOLING_STOP_SETTINGS = "cooling_stop_settings"  # 冷房停止時の設定
                COOLING_SETTINGS = "cooling_settings"  # 冷房時の設定

            def __init__(self, config):
                self.config = config
                # 露点制御しない場合の温度を初期化
                self.condensation_prevention_threshold = self.config[
                    self._Settings.CONDENSATION_PREVENTION_THRESHOLD.value
                ]
                # 冷房時のPMV閾値を初期化
                self.pmv_threshold_for_cooling = self.config[self._Settings.PMV_THRESHOLD_FOR_COOLING.value]
                # 冷房停止時の設定を初期化
                self.cooling_stop_settings = self._CoolingStopSettings(
                    self.config[self._Settings.COOLING_SETTINGS.value]
                ).aircon_state
                # 冷房時の設定を初期化
                self.cooling_settings = self._CoolingSettings(
                    self.config[self._Settings.COOLING_SETTINGS.value]
                ).aircon_state

            class _CoolingStopSettings(_BaseAirconSettings):
                """冷房停止時の設定項目を定義する列挙型"""

            class _CoolingSettings(_BaseAirconSettings):
                """冷房時の設定項目クラス"""

    class _WeakestAirconSettings:
        """最弱エアコン設定項目を定義する列挙型"""

        class _Settings(Enum):
            """最弱エアコン設定項目を定義する列挙型"""

            COOLING_SETTINGS = "cooling_settings"  # 冷房時の設定
            HEATING_SETTINGS = "heating_settings"  # 暖房時の設定

        def __init__(self, config):
            self.config = config
            # 冷房時の設定を初期化
            self.cooling_settings = self._CoolingSettings(
                self.config[self._Settings.COOLING_SETTINGS.value]
            ).aircon_state
            # 暖房時の設定を初期化
            self.heating_settings = self._HeatingSettings(
                self.config[self._Settings.HEATING_SETTINGS.value]
            ).aircon_state

        class _CoolingSettings(_BaseAirconSettings):
            """冷房時の設定項目クラス"""

        class _HeatingSettings(_BaseAirconSettings):
            """暖房時の設定項目クラス"""
