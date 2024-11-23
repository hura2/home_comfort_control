import datetime
import logging
import unicodedata
from io import StringIO
from typing import Optional, Tuple

from api.notify.notify_factory import NotifyFactory
from common import constants
from logger.log_messages import LogMessages
from models.aircon_state import AirconState
from models.circulator_state import CirculatorState
from models.comfort_factors import ComfortFactors
from models.home_sensor import HomeSensor
from models.pmv_result import PMVResult
from models.sensor import Sensor

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
    def logs_notify():
        """
        バッファに蓄積されたログを送信します。
        """
        # バッファの内容を取得
        log_content = log_buffer.getvalue()

        if not log_content.strip():
            SystemEventLogger.log_info("ログが空のため、メールは送信されません。")
            return

        NotifyFactory.create_manager().notify(log_content)

    @staticmethod
    def reset_log_buffer():
        """
        バッファをリセットします。
        """
        log_buffer.truncate(0)
        log_buffer.seek(0)

    @staticmethod
    def log_info(message_template: str, **kwargs):
        """
        指定されたテンプレートに動的な値を埋め込み、ログに出力する。

        Args:
            message_template (str): メッセージテンプレート
            **kwargs: テンプレートに埋め込むデータ
        """
        message = message_template.format(**kwargs)
        logger.info(message)
    @staticmethod
    def log_error(message_template: str, **kwargs):
        """
        エラーメッセージをログに出力します。

        Args:
            message_template (str): メッセージテンプレート
            **kwargs: テンプレートに埋め込むデータ
        """
        message = message_template.format(**kwargs)
        logger.error(message)
        
        # エラーが記録されたことをフラグで追跡
        SystemEventLogger.error_logged = True

    @staticmethod
    def check_and_notify():
        """
        エラーが記録されていた場合、通知を送信します。
        """
        if SystemEventLogger.error_logged:
            SystemEventLogger.logs_notify()
            # 通知後はフラグをリセット
            SystemEventLogger.error_logged = False

    @staticmethod
    def _log_sensor_data(sensor: Sensor, reference_sensor: Optional[Sensor] = None):
        """
        指定されたセンサーの情報をログに出力します。
        CO2センサーの場合は、温度差も表示します。

        :param sensor: ログに出力するセンサー
        :param reference_sensor: 温度差を表示する場合の参照センサー（省略可能）
        """
        # 基本センサー情報を整形
        sensor_info = LogMessages.SENSOR_DATA.format(
            label=SystemEventLogger._left(8, sensor.label),
            location=SystemEventLogger._left(4, sensor.location),
            temperature=sensor.air_quality.temperature,
            humidity=sensor.air_quality.humidity,
            absolute_humidity=sensor.air_quality.absolute_humidity,
        )

        # 温度差を表示する場合、参照センサーと比較
        if reference_sensor:
            temp_diff = abs(
                reference_sensor.air_quality.temperature - sensor.air_quality.temperature
            )
            sensor_info += ", " + LogMessages.TEMP_DIFF.format(
                reference_label=reference_sensor.label,
                reference_location=reference_sensor.location,
                temp_diff=temp_diff,
            )

        # CO2センサーの場合、CO2レベルも表示
        if sensor.type == constants.SensorType.CO2:
            sensor_info += ", " + LogMessages.CO2_SENSOR.format(
                co2_level=sensor.air_quality.co2_level
            )

        # 最後にログ出力
        SystemEventLogger.log_info(sensor_info)

    @staticmethod
    def log_environment_data(
        home_sensor: HomeSensor,
        forecast_max_temperature: int,
        now: datetime.datetime,
    ):
        """
        環境情報をログに出力します。

        Args:
            home_sensor (HomeSensor): 家の温度と湿度データ
            forecast_max_temperature (int): 最高気温予報
            now (datetime.datetime): 現在時刻
        """
        # 現在時刻と最高気温予報をログに出力
        SystemEventLogger.log_info(
            LogMessages.CURRENT_TIME, current_time=now.strftime("%Y-%m-%d %H:%M:%S")
        )
        SystemEventLogger.log_info(
            LogMessages.FORECAST_MAX_TEMP, forecast_max_temperature=forecast_max_temperature
        )

        # CO2濃度があれば出力
        if home_sensor.main_co2_level:
            SystemEventLogger.log_info(LogMessages.CO2_LEVEL, co2_level=home_sensor.main_co2_level)

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
            LogMessages.SURFACE_TEMPERATURES,
            wall=pmv.wall,
            ceiling=pmv.ceiling,
            floor=pmv.floor,
            mrt=pmv.mean_radiant_temperature,
        )

        SystemEventLogger.log_info(
            LogMessages.SENSIBLE_TEMP,
            sensible_temperature=(pmv.dry_bulb_temperature + pmv.mean_radiant_temperature) / 2,
        )

        SystemEventLogger.log_info(
            LogMessages.MET_ICL_VALUES, met=comfort_factors.met, icl=comfort_factors.icl
        )

        SystemEventLogger.log_info(
            LogMessages.RELATIVE_AIR_SPEED, relative_air_speed=pmv.relative_air_speed
        )

        SystemEventLogger.log_info(
            LogMessages.DYNAMIC_CLOTHING,
            dynamic_clothing_insulation=pmv.dynamic_clothing_insulation,
        )

        SystemEventLogger.log_info(LogMessages.PMV_PPD, pmv=pmv.pmv, ppd=pmv.ppd)

    @staticmethod
    def log_elapsed_time(hours: int, minutes: int):
        """
        エアコン設定の経過時間をログに出力します。

        Args:
            hours (int): 経過時間の時間部分
            minutes (int): 経過時間の分部分
        """
        SystemEventLogger.log_info(LogMessages.ELAPSED_TIME, hours=hours, minutes=minutes)

    @staticmethod
    def log_aircon_state(aircon_state: AirconState, current_aircon_state: AirconState):
        """
        エアコンの状態変更をログに出力します。

        Args:
            aircon_state (AirconState): 変更後のエアコンの状態。
            current_aircon_state (AirconState): 現在のエアコンの状態。
        """
        if current_aircon_state is None:
            SystemEventLogger.log_info(
                LogMessages.AIRCON_STATE_INIT,
                new_state=SystemEventLogger.format_state(aircon_state),
            )
        else:
            SystemEventLogger.log_info(
                LogMessages.AIRCON_STATE_CHANGE,
                current_state=SystemEventLogger.format_state(current_aircon_state),
                new_state=SystemEventLogger.format_state(aircon_state),
            )

    @staticmethod
    def log_circulator_state(
        current_circulator_state: CirculatorState, circulator_state: CirculatorState
    ):
        """
        サーキュレーターの状態をログに出力します。

        Args:
            current_circulator_state (CirculatorState): サーキュレーターの電源
            fan_speed (str): サーキュレーターの設定された風量
        """
        SystemEventLogger.log_info(
            LogMessages.CIRCULATOR_STATUS,
            power=current_circulator_state.power.description,
            fan_speed=current_circulator_state.fan_speed,
        )
        SystemEventLogger.log_info(
            LogMessages.CIRCULATOR_SETTINGS_SUCCESS,
            power=circulator_state.power.description,
            fan_speed=circulator_state.fan_speed,
        )

        # テスト用コード
        if (
            current_circulator_state.power == constants.CirculatorPower.OFF
            and circulator_state.fan_speed > 0
        ):
            notify_manager = NotifyFactory.create_manager()
            notify_manager.notify(f"サーキュレーターの風量を{circulator_state.fan_speed}に設定")
        if (
            current_circulator_state.power == constants.CirculatorPower.ON
            and circulator_state.fan_speed == 0
        ):
            notify_manager = NotifyFactory.create_manager()
            notify_manager.notify("サーキュレーターの電源をOFFに設定")

    @staticmethod
    def log_aircon_scores(scores: Tuple[int, int, int, int, int]):
        """
        エアコンのスコアをログに出力します。

        Args:
            scores (Tuple[int, int, int, int, int]): 先々週、先週、今週、昨日、今日のスコア
        """
        SystemEventLogger.log_info(
            LogMessages.AIRCON_SCORES,
            week_before_last_score=scores[0],
            last_week_score=scores[1],
            this_week_score=scores[2],
            yesterday_score=scores[3],
            today_score=scores[4],
        )

    @staticmethod
    def log_exception(e: Exception):
        """
        例外発生時のログを出力します。

        Args:
            e (Exception): 発生した例外
        """
        SystemEventLogger.log_info(LogMessages.EXCEPTION_OCCURRED, exception_message=str(e))

    @staticmethod
    def format_state(state: AirconState) -> str:
        """
        エアコンの状態を文字列にフォーマットします。

        Args:
            state (AirconState): エアコンの状態。

        Returns:
            str: フォーマットされたエアコンの状態。
        """
        return f"{state.mode.description}:{state.temperature}:{state.fan_speed.description}:{state.power.description}"

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
