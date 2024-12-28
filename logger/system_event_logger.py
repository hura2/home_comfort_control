import inspect
import logging
import unicodedata
from datetime import timezone
from io import StringIO
from typing import Tuple, Type

import i18n

from api.notify.notify_factory import NotifyFactory
from models.weather_forecast_hourly_model import WeatherForecastHourlyModel
from settings import DB_TZ, LOCAL_TZ
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.circulator_settings import CirculatorSettings
from shared.dataclass.comfort_factors import ComfortFactors
from shared.dataclass.home_sensor import HomeSensor
from shared.dataclass.pmv_result import PMVResult
from shared.dataclass.sensor import Sensor
from shared.enums.power_mode import PowerMode
from shared.enums.sensor_type import SensorType
from util.string_helper import StringHelper
from util.time_helper import TimeHelper

# 通常のフォーマッタ
formatter = logging.Formatter("%(message)s")

# 通常ログのハンドラー（コンソール出力）
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# メール送信用バッファ
log_buffer = StringIO()
buffer_handler = logging.StreamHandler(log_buffer)
buffer_handler.setFormatter(formatter)

# ロガーの設定
logger = logging.getLogger("SystemEventLogger")
logger.propagate = False
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)  # 通常ログ用
logger.addHandler(buffer_handler)  # メール送信用


class SystemEventLogger:
    """
    ログ関連のユーティリティ
    """

    # エラーが記録されたかどうかを追跡するフラグ
    error_logged = False

    @staticmethod
    def get_buffered_logs():
        """
        バッファに蓄積されたログを取得します。
        """
        # バッファの内容を取得
        log_content = log_buffer.getvalue()

        if not log_content.strip():
            SystemEventLogger.log_info("ログが空のため、メールは送信されません。")
            return

        return log_content

    @staticmethod
    def reset_log_buffer():
        """
        バッファをリセットします。
        """
        log_buffer.truncate(0)
        log_buffer.seek(0)

    @staticmethod
    def log_info(message_key: str, **kwargs):
        """
        指定されたテンプレートに動的な値を埋め込み、ログに出力する。

        Args:
            message_key (str): メッセージKey
            **kwargs: テンプレートに埋め込むデータ
        """
        # print(f"log.{message_key}")
        message = i18n.t(f"log.{message_key}", **kwargs)
        logger.info(message)

    @staticmethod
    def log_error(
        class_type: Type | None = None,
        **kwargs,
    ):
        """
        エラーメッセージをログに出力します。

        Args:
            class_type (Type | None): エラーが発生したクラス名
            **kwargs: テンプレートに埋め込むデータ
        """
        class_name = ""
        # 呼び出し元の情報を取得
        stack = inspect.stack()[1]  # 呼び出し元のフレームを取得
        if class_type is None:
            class_name = (
                stack.frame.f_locals.get("self", None).__class__.__name__
                if "self" in stack.frame.f_locals
                else None
            )
        else:
            class_name = class_type.__name__
            method_name = stack.function

        if class_name:
            message_key = f"{StringHelper.camel_to_snake(class_name)}.{method_name}"
        else:
            message_key = method_name  # クラスがない場合はメソッド名のみ

        # 翻訳ファイルからエラーメッセージを取得
        message = i18n.t(key=f"error.{message_key}", **kwargs)

        logger.error(message)

        # エラーが記録されたことをフラグで追跡
        SystemEventLogger.error_logged = True

    @staticmethod
    def check_error():
        """
        エラーが記録されたかどうかを判断します。
        """
        return SystemEventLogger.error_logged

    @staticmethod
    def _log_sensor_data(sensor: Sensor, reference_sensor: Sensor | None = None):
        """
        指定されたセンサーの情報をログに出力します。
        CO2センサーの場合は、温度差も表示します。

        :param sensor: ログに出力するセンサー
        :param reference_sensor: 温度差を表示する場合の参照センサー（省略可能）
        """
        # 基本センサー情報を整形
        sensor_info = i18n.t(
            "log.environment_data.sensor_data",
            label=SystemEventLogger._left(8, sensor.label),
            location=SystemEventLogger._left(4, sensor.location),
            temperature=f"{sensor.air_quality.temperature:>5.1f}",
            humidity=f"{sensor.air_quality.humidity:>5.1f}",
            absolute_humidity=f"{sensor.air_quality.absolute_humidity:>6.2f}",
        )

        # 温度差を表示する場合、参照センサーと比較
        if reference_sensor:
            temp_diff = abs(
                reference_sensor.air_quality.temperature - sensor.air_quality.temperature
            )
            sensor_info += ", " + i18n.t(
                "log.environment_data.temp_diff",
                reference_label=reference_sensor.label,
                reference_location=reference_sensor.location,
                temp_diff=f"{temp_diff:>5.1f}",
            )

        # CO2センサーの場合、CO2レベルも表示
        if sensor.type == SensorType.CO2:
            sensor_info += ", " + i18n.t(
                "log.environment_data.co2_level", co2_level=sensor.air_quality.co2_level
            )

        # 最後にログ出力
        logger.info(sensor_info)

    @staticmethod
    def log_environment_data(
        home_sensor: HomeSensor,
        forecast_max_temperature: float | None,
        closest_future_forecast: WeatherForecastHourlyModel | None,
    ):
        """
        環境情報をログに出力します。

        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            forecast_max_temperature (int): 最高気温予報
        """
        # 現在時刻と最高気温予報をログに出力
        SystemEventLogger.log_info(
            i18n.t("time_related.current_time"),
            current_time=TimeHelper.get_current_time().strftime("%Y-%m-%d %H:%M:%S"),
        )
        SystemEventLogger.log_info(
            i18n.t("time_related.forecast_max_temp"),
            forecast_max_temperature=forecast_max_temperature,
        )
        if closest_future_forecast:
            SystemEventLogger.log_closest_forecast_after(closest_future_forecast)
        # CO2濃度があれば出力
        if home_sensor.main_co2_level:
            SystemEventLogger.log_info(
                i18n.t("environment_data.co2_level"), co2_level=home_sensor.main_co2_level
            )

        # メインセンサーの情報をログに出力
        SystemEventLogger._log_sensor_data(home_sensor.main)

        # サブセンサーの情報をログに出力（存在すれば）
        if home_sensor.sub:
            SystemEventLogger._log_sensor_data(home_sensor.sub, home_sensor.main)

        # 補助センサーの情報をログに出力（存在すれば）
        if home_sensor.supplementaries:
            for supplementary in home_sensor.supplementaries:
                SystemEventLogger._log_sensor_data(supplementary, home_sensor.main)

        # 室内センサーの平均の情報をログに出力
        SystemEventLogger._log_sensor_data(home_sensor.average_indoor_sensor)

        # 屋外センサーの情報をログに出力（存在すれば）
        if home_sensor.outdoor:
            SystemEventLogger._log_sensor_data(
                home_sensor.outdoor, home_sensor.average_indoor_sensor
            )

    @staticmethod
    def log_pmv(pmv: PMVResult, comfort_factors: ComfortFactors):
        """
        PMV計算の結果をログに出力します。

        Args:
            pmv (PMVResult): PMV計算の結果
            comfort_factors (ComfortFactors): コンフォーマンス因子の値
        """
        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.surface_temperatures"),
            wall=f"{pmv.wall:.1f}",
            ceiling=f"{pmv.ceiling:.1f}",
            floor=f"{pmv.floor:.1f}",
            mrt=f"{pmv.mean_radiant_temperature:.1f}",
        )

        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.sensible_temp"),
            sensible_temperature=f"{(pmv.dry_bulb_temperature + pmv.mean_radiant_temperature) / 2:.1f}",
        )

        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.met_icl_values"),
            met=f"{comfort_factors.met:.1f}",
            icl=f"{comfort_factors.clo:.1f}",
        )

        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.relative_air_speed"),
            relative_air_speed=f"{pmv.relative_air_speed:.1f}",
        )

        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.dynamic_clothing"),
            dynamic_clothing_insulation=f"{pmv.dynamic_clothing_insulation:.1f}",
        )

        SystemEventLogger.log_info(
            i18n.t("pmv_calculation.pmv_ppd"), pmv=f"{pmv.pmv:.1f}", ppd=f"{pmv.ppd:.1f}"
        )

    @staticmethod
    def log_elapsed_time(hours: int, minutes: int):
        """
        エアコン設定の経過時間をログに出力します。

        Args:
            hours (int): 経過時間の時間部分
            minutes (int): 経過時間の分部分
        """
        SystemEventLogger.log_info(
            i18n.t("aircon_related.elapsed_time"), hours=hours, minutes=minutes
        )

    @staticmethod
    def log_aircon_settings(
        aircon_settings: AirconSettings, current_aircon_settings: AirconSettings | None = None
    ):
        """
        エアコンの状態変更をログに出力します。

        Args:
            aircon_settings (AirconSettings): 変更後のエアコンの状態。
            current_aircon_settings (AirconSettings): 現在のエアコンの状態。
        """
        if current_aircon_settings is None:
            SystemEventLogger.log_info(
                i18n.t("aircon_related.aircon_settings_init"),
                new_settings=SystemEventLogger.format_settings(aircon_settings),
            )
        else:
            SystemEventLogger.log_info(
                i18n.t("aircon_related.aircon_settings_change"),
                current_settings=SystemEventLogger.format_settings(current_aircon_settings),
                new_settings=SystemEventLogger.format_settings(aircon_settings),
            )

    @staticmethod
    def log_circulator_settings(
        current_circulator_settings: CirculatorSettings, circulator_settings: CirculatorSettings
    ):
        """
        サーキュレーターの状態をログに出力します。

        Args:
            current_circulator_settings (CirculatorSettings): サーキュレーターの電源
            fan_speed (str): サーキュレーターの設定された風量
        """
        SystemEventLogger.log_info(
            i18n.t("circulator_related.circulator_status"),
            power=current_circulator_settings.power.label,
            fan_speed=current_circulator_settings.fan_speed,
        )
        SystemEventLogger.log_info(
            i18n.t("circulator_related.circulator_settings_success"),
            power=circulator_settings.power.label,
            fan_speed=circulator_settings.fan_speed,
        )

        # テスト用コード
        if current_circulator_settings.power == PowerMode.OFF and circulator_settings.fan_speed > 0:
            notify_manager = NotifyFactory.create_manager()
            notify_manager.notify_important(
                f"サーキュレーターの風量を{circulator_settings.fan_speed}に設定"
            )
        if current_circulator_settings.power == PowerMode.ON and circulator_settings.fan_speed == 0:
            notify_manager = NotifyFactory.create_manager()
            notify_manager.notify_important("サーキュレーターの電源をOFFに設定")

    @staticmethod
    def log_aircon_scores(scores: Tuple[int, int, int, int, int]):
        """
        エアコンのスコアをログに出力します。

        Args:
            scores (Tuple[int, int, int, int, int]): 先々週、先週、今週、昨日、今日のスコア
        """
        SystemEventLogger.log_info(
            i18n.t("aircon_related.aircon_scores"),
            week_before_last_score=scores[0],
            last_week_score=scores[1],
            this_week_score=scores[2],
            yesterday_score=scores[3],
            today_score=scores[4],
        )

    @staticmethod
    def log_closest_forecast_after(weather_forecast_hourly_model: WeatherForecastHourlyModel):
        """
        最近の天気予報をログに出力します。

        Args:
            weather_forecast_hourly_model (WeatherForecastHourlyModel): 最近の天気予報
        """
        SystemEventLogger.log_info(
            i18n.t("aircon_related.closest_forecast_after"),
            forecast_time=weather_forecast_hourly_model.forecast_time.replace(tzinfo=DB_TZ)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %H:%M:%S"),
            temperature=weather_forecast_hourly_model.temperature,
            # cloud_percentageがNoneの場合はデフォルト値を使用
            cloud_percentage=(
                weather_forecast_hourly_model.cloud_percentage * 100
                if weather_forecast_hourly_model.cloud_percentage is not None
                else "N/A"
            ),
            weather=weather_forecast_hourly_model.weather,
        )

    @staticmethod
    def log_solar_utilization_heating_reduction():
        """
        日射利用率の温暖化削減をログに出力します。
        """
        SystemEventLogger.log_info(i18n.t("aircon_related.solar_utilization.heating_reduction"))

    @staticmethod
    def log_exception(e: Exception):
        """
        例外発生時のログを出力します。

        Args:
            e (Exception): 発生した例外
        """
        logger.error(str(e))

    @staticmethod
    def format_settings(aircon_settings: AirconSettings) -> str:
        """
        エアコンの状態を文字列にフォーマットします。

        Args:
            aircon_settings (AirconSettings): エアコンの状態。

        Returns:
            str: フォーマットされたエアコンの状態。
        """
        return f"{aircon_settings.mode.value.label}:{aircon_settings.temperature}:{aircon_settings.fan_speed.value.label}:{aircon_settings.power.value.label}"

    @staticmethod
    def _left(digit, msg):
        """
        文字列を左揃えにする

        Args:
            digit (int): 表示する文字数
            msg (str): 表示する文字列

        Returns:
            str: 左揃えされた文字列
        """
        # 文字列の長さを取得
        digit = max(digit, len(msg))
        # 文字列の幅を取得
        for c in msg:
            # 半角文字は1文字、全角文字は2文字
            if unicodedata.east_asian_width(c) in ("F", "W", "A"):
                digit -= 2
            else:
                digit -= 1
        # 必要な桁数分の全角スペースを追加
        # 2で割ることで、全角スペースの必要数に調整
        return msg + "\u3000" * (digit // 2)
