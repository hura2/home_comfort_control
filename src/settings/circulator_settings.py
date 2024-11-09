from pathlib import Path

import yaml


class CirculatorSettings:
    """
    サーキュレーター設定を管理するクラス。

    このクラスは設定ファイル（YAML形式）からサーキュレーターに関連する設定値を読み込み、
    その値をプロパティとして取得できるように提供します。
    """

    class _TemperatureSettings:
        """温度設定項目を定義する列挙型"""

        TEMPERATURE_SETTINGS = "temperature_settings"  # 温度設定
        HIGH_SPEED_THRESHOLDS = "high_speed_thresholds"  # 高温時のスピード
        NORMAL_SPEED_THRESHOLDS = "normal_speed_thresholds"  # 高温以外の時のスピード

    def __init__(self):
        # 設定ファイルのパスを定義
        self.config_file = Path(__file__).parent.parent / "yaml" / "circulator_settings.yaml"
        # 設定をロード
        self.config = self._load_config()

    def _load_config(self):
        # YAMLファイルを読み込み、設定を返す
        with open(self.config_file, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    @property
    def high_speed_thresholds(self):
        """高温時のスピード設定を取得"""
        return self.config[self._TemperatureSettings.TEMPERATURE_SETTINGS][
            self._TemperatureSettings.HIGH_SPEED_THRESHOLDS
        ]

    @property
    def normal_speed_thresholds(self):
        """高温以外の時のスピード設定を取得"""
        return self.config[self._TemperatureSettings.TEMPERATURE_SETTINGS][
            self._TemperatureSettings.NORMAL_SPEED_THRESHOLDS
        ]


# 使用例
# if __name__ == "__main__":
#     settings = CirculatorSettings()
#     print("High Speed Thresholds:", settings.high_speed_thresholds)
#     print("Normal Speed Thresholds:", settings.normal_speed_thresholds)
