import datetime
import time
from enum import Enum
from pathlib import Path

import yaml


class ClothingActivityByTemperatureSettings:
    """
    温度に基づく衣服活動設定を管理するクラス。

    高温時と低温時の設定を含む設定ファイル（YAML形式）を読み込み、
    それぞれの設定をプロパティとして取得できるように提供します。
    """

    class _Settings(Enum):
        """設定項目を定義する列挙型"""

        HIGH_TEMP_SETTINGS = "high_temp_settings"  # 高温時の設定
        LOW_TEMP_SETTINGS = "low_temp_settings"  # 低温時の設定

    def __init__(self):
        # 設定ファイルのパスを定義

        self.config_file = (
            Path(__file__).parent.parent / "yaml" / "clothing_activity_by_temperature_settings.yaml"
        )
        # 設定をロード
        self.config = self._load_config()
        # 高温時の設定を初期化
        self.high_temp_settings = self._HighTempSettings(
            self.config[self._Settings.HIGH_TEMP_SETTINGS.value]
        )
        # 低温時の設定を初期化
        self.low_temp_settings = self._LowTempSettings(
            self.config[self._Settings.LOW_TEMP_SETTINGS.value]
        )

    def _load_config(self):
        # YAMLファイルを読み込み、設定を返す
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    class _HighTempSettings:
        """高温時の設定を管理するクラス"""

        class _Settings(Enum):
            """設定項目を定義する列挙型"""

            MET = "met"  # 代謝量に関する設定
            ICL = "icl"  # 衣服熱抵抗に関する設定
            TIME_SETTINGS = "time_settings"  # 時間帯に関する設定

        def __init__(self, config):
            self.config = config
            self.met = self._MetSettings(self.config[self._Settings.MET.value])
            self.icl = self._IclSettings(self.config[self._Settings.ICL.value])
            self.time_settings = self._TimeSettings(self.config[self._Settings.TIME_SETTINGS.value])

        class _MetSettings:
            """代謝量設定を管理するクラス"""

            def __init__(self, config):
                self.config = config

            @property
            def daytime(self) -> float:
                """日中の代謝量を取得"""
                return self.config["daytime"]

            @property
            def bedtime(self) -> float:
                """就寝時の代謝量を取得"""
                return self.config["bedtime"]

        class _IclSettings:
            """衣服熱抵抗設定を管理するクラス"""

            def __init__(self, config):
                self.config = config

            @property
            def daytime(self) -> float:
                """日中の衣服熱抵抗を取得"""
                return self.config["daytime"]

            @property
            def bedtime(self) -> float:
                """就寝時の衣服熱抵抗を取得"""
                return self.config["bedtime"]

        class _TimeSettings:
            """時間帯設定を管理するクラス"""

            def __init__(self, config):
                self.config = config
                self.lunch_time = self._TimePeriod(config.get("lunch_time", {}))
                self.dinner_time = self._TimePeriod(config.get("dinner_time", {}))
                self.pre_bedtime = self._TimePeriod(config.get("pre_bedtime", {}))

            class _TimePeriod:
                """時間帯設定を管理するクラス"""

                class _Settings(Enum):
                    """設定項目を定義する列挙型"""

                    START = "start"
                    END = "end"
                    MET = "met"
                    USE = "use"

                def __init__(self, config):
                    self.config = config

                @property
                def start(self) -> time:
                    """開始時間を取得"""
                    hour, minute = map(int, self.config[self._Settings.START.value].split(":"))
                    return datetime.time(hour, minute)

                @property
                def end(self) -> time:
                    """終了時間を取得"""
                    hour, minute = map(int, self.config[self._Settings.END.value].split(":"))
                    return datetime.time(hour, minute)

                @property
                def met(self) -> float:
                    """加算代謝量を取得"""
                    return self.config.get(self._Settings.MET.value, 0.0)

                @property
                def use(self) -> bool:
                    """設定を使用するかどうかのフラグを取得"""
                    return self.config.get(self._Settings.USE.value, False)

    class _LowTempSettings:
        """低温時の設定を管理するクラス"""

        class _Settings(Enum):
            """設定項目を定義する列挙型"""

            MET = "met"  # 代謝量に関する設定
            ICL = "icl"  # 衣服熱抵抗に関する設定
            TIME_SETTINGS = "time_settings"  # 時間帯に関する設定

        def __init__(self, config):
            self.config = config
            self.met = self._MetSettings(self.config[self._Settings.MET.value])
            self.icl = self._IclSettings(self.config[self._Settings.ICL.value])
            self.time_settings = self._TimeSettings(self.config[self._Settings.TIME_SETTINGS.value])

        class _MetSettings:
            """代謝量設定を管理するクラス"""

            def __init__(self, config):
                self.config = config

            @property
            def daytime(self) -> float:
                """日中の代謝量を取得"""
                return self.config["daytime"]

            @property
            def bedtime(self) -> float:
                """就寝時の代謝量を取得"""
                return self.config["bedtime"]

        class _IclSettings:
            """衣服熱抵抗設定を管理するクラス"""

            def __init__(self, config):
                self.config = config

            @property
            def daytime(self) -> float:
                """日中の衣服熱抵抗を取得"""
                return self.config["daytime"]

            @property
            def bedtime(self) -> float:
                """就寝時の衣服熱抵抗を取得"""
                return self.config["bedtime"]

        class _TimeSettings:
            """時間帯設定を管理するクラス"""

            def __init__(self, config):
                self.config = config
                self.heating = self._HeatingSettings(config.get("heating", {}))

            class _HeatingSettings:
                """暖房時の設定を管理するクラス"""

                def __init__(self, config):
                    self.config = config
                    self.use = self.config.get("use", False)
                    self.high_costs = [self._TimePeriod(time) for time in config.get("high_cost", {})]
                    self.low_costs = [self._TimePeriod(time) for time in config.get("low_cost", {})]

                class _TimePeriod:
                    """時間帯の調整設定を管理するクラス"""

                    class _Settings(Enum):
                        """設定項目を定義する列挙型"""

                        START = "start"
                        END = "end"
                        ADJUSTMENT = "adjustment"

                    def __init__(self, config):
                        self.config = config

                    @property
                    def start(self) -> time:
                        """開始時間を取得"""
                        hour, minute = map(int, self.config[self._Settings.START.value].split(":"))
                        return datetime.time(hour, minute)

                    @property
                    def end(self) -> time:
                        """終了時間を取得"""
                        hour, minute = map(int, self.config[self._Settings.END.value].split(":"))
                        return datetime.time(hour, minute)


                    @property
                    def adjustment(self) -> float:
                        """調整値を取得"""
                        return self.config.get("adjustment", 0.0)
