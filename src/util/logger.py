import datetime
import logging
import unicodedata
from typing import Tuple

from common import constants
from common.data_types import AirconState, CirculatorState, ComfortFactors, HomeSensor, PMVResults, Sensor

formatter = "%(message)s"
logging.basicConfig(level=logging.INFO, format=formatter)

logger = logging.getLogger(__name__)


class LoggerUtil:
    """
    ログ関連のユーティリティ
    """

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
        logger.info(f"現在時刻: {now}")
        logger.info(f"最高気温予報: {forecast_max_temperature}°")

        # CO2濃度があれば出力
        if home_sensor.main_co2_level:
            logger.info(f"CO2濃度: {home_sensor.main_co2_level}ppm")

        # メインセンサーの情報をログに出力
        LoggerUtil._log_sensor_data(home_sensor.main)

        # サブセンサーの情報をログに出力（存在すれば）
        if home_sensor.sub:
            LoggerUtil._log_sensor_data(home_sensor.sub, home_sensor.main)

        # 補助センサーの情報をログに出力（存在すれば）
        if home_sensor.supplementaries:
            for supplementary in home_sensor.supplementaries:
                LoggerUtil._log_sensor_data(supplementary, home_sensor.main)

        # 室内センサーの平均の情報をログに出力
        LoggerUtil._log_sensor_data(home_sensor.average_indoor_sensor)

        # 屋外センサーの情報をログに出力（存在すれば）
        if home_sensor.outdoor:
            LoggerUtil._log_sensor_data(home_sensor.outdoor)

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

    def _log_sensor_data(sensor: Sensor, reference_sensor: Sensor = None):
        """
        指定されたセンサーの情報をログに出力します。
        CO2センサーの場合は、温度差も表示します。

        :param sensor: ログに出力するセンサー
        :param reference_sensor: 温度差を表示する場合の参照センサー（省略可能）
        """
        # ラベルとセンサー位置を左揃えで指定
        sensor_info = f"{LoggerUtil._left(8, sensor.label)}:{LoggerUtil._left(4,sensor.location)}: "

        # 温度、湿度を表示
        sensor_info += f"温度{sensor.air_quality.temperature:>5.1f}°, 湿度{sensor.air_quality.humidity:>5.1f}%, 絶対湿度{sensor.air_quality.absolute_humidity:>6.2f}g/㎥"

        # 温度差の計算と表示（参照センサーがある場合）
        if reference_sensor:
            temp_diff = abs(reference_sensor.air_quality.temperature - sensor.air_quality.temperature)
            sensor_info += f", {reference_sensor.label}との温度差{temp_diff:.1f}°"

        # CO2センサーのログ
        if sensor.type == constants.SensorType.CO2:
            sensor_info += f", CO2: {sensor.air_quality.co2_level:1d}ppm"

        logger.info(sensor_info)

    @staticmethod
    def log_pmv_results(pmv: PMVResults, comfort_factors: ComfortFactors):
        """
        PMV計算の結果をログに出力します。

        Args:
            pmv (PMVCalculation): PMV計算の結果
            comfort_factors (ComfortFactors): コンフォーマンス因子の値
        """
        logger.info(
            f"表面温度:壁 {pmv.wall:.1f}°, 天井 {pmv.ceiling:.1f}°, 床 {pmv.floor:.1f}°, 平均放射温度: {pmv.mean_radiant_temperature:.1f}°"
        )
        logger.info(f"体感温度: {(pmv.dry_bulb_temperature + pmv.mean_radiant_temperature) / 2:.1f}°")
        logger.info(f"met: {comfort_factors.met}, icl: {comfort_factors.icl:.2f}")
        logger.info(f"相対風速: {pmv.relative_air_speed:.1f}m/s")
        logger.info(f"動的な衣服の断熱性: {pmv.dynamic_clothing_insulation:.2f}")
        logger.info(f"pmv = {pmv.pmv}, ppd = {pmv.ppd}%")

    @staticmethod
    def log_elapsed_time(hours, minutes):
        """
        エアコン設定の経過時間をログに出力します。

        Args:
            hours (int): 経過時間の時間部分
            minutes (int): 経過時間の分部分
        """
        logger.info(f"前回のエアコン設定からの経過: {hours}時間{minutes}分")

    @staticmethod
    def log_aircon_state(aircon_state: AirconState):
        """
        エアコンの状態をログに出力します。

        Args:
            aircon_state (AirconState): エアコンの状態
        """
        logger.info(
            f"{aircon_state.mode.description}:{aircon_state.temperature}:{aircon_state.fan_speed.description}:{aircon_state.power.description}"
        )

    @staticmethod
    def log_circulator_state(current_circulator_state: CirculatorState, fan_speed: str):
        """
        サーキュレーターの状態をログに出力します。

        Args:
            current_circulator_state (CirculatorState): サーキュレーターの電源
            fan_speed (str): サーキュレーターの設定された風量
        """
        logger.info(f"現在のサーキュレーターの電源:{current_circulator_state.power.description}")
        logger.info(f"現在のサーキュレーターの風量:{current_circulator_state.fan_speed}")
        logger.info(f"サーキュレーターの風量を{fan_speed}に設定")

    @staticmethod
    def log_aircon_scores(scores: Tuple[int, int, int, int]):
        """
        エアコンのスコアをログに出力します。

        Args:
            scores (Tuple[int, int, int, int]): 先々週、先週、今週、昨日、今日のスコア
        """
        logger.info(f"先々週のスコア平均: {scores[0]}")
        logger.info(f"先週のスコア平均: {scores[1]}")
        logger.info(f"今週のスコア平均: {scores[2]}")
        logger.info(f"昨日のスコア: {scores[3]}")
        logger.info(f"今日のスコア予想: {scores[4]}")
