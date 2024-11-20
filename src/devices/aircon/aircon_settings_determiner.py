from common import constants
from models.aircon_state import AirconState
from models.home_sensor import HomeSensor
from models.pmv_result import PMVResult
from settings.aircon_settings import AirconSettings
from settings.general_settings import GeneralSettings
from util.logger import logger


class AirconSettingsDeterminer:
    """
    エアコンの設定を決定するクラス
    """

    # エアコンの動作を設定する関数
    @staticmethod
    def determine_aircon_settings(
        pmvResult: PMVResult,
        home_sensor: HomeSensor,
        is_sleeping: bool,
    ):
        """
        エアコンの設定を決定するメソッド
        Args:
            pmvResult (PMVResult): PMV計算結果を持つオブジェクト。
            home_sensor (HomeSensor): 家庭の環境情報を格納したオブジェクト。
            is_sleeping (bool): 寝ている時間。
        Returns:
            constants.AirconState: 設定されたエアコンの設定。
        """
        # エアコンの設定を決定
        aircon_state = AirconSettingsDeterminer._get_aircon_state_for_pmv(pmvResult.pmv)
        aircon_state = AirconSettingsDeterminer._get_aircon_state_for_conditions(
            aircon_state, pmvResult, home_sensor, is_sleeping
        )
        return aircon_state

    # pmvによってエアコンの設定を判定
    @staticmethod
    def _get_aircon_state_for_pmv(pmv: float) -> AirconState:
        """
        pmvによってエアコンの設定を判定するメソッド
        Args:
            pmv (float): PMV値。
        Returns:
            constants.AirconState: 設定されたエアコンの設定。
        """
        aircon_settings = AirconSettings()
        aircon_state = AirconState()

        # pmvによってエアコンの設定を判定
        found_threshold = False  # 条件を満たすデータが見つかったかどうか

        for pmv_threshold in aircon_settings.pmv_threshold_settings.pmv_thresholds:
            if pmv <= pmv_threshold.threshold:
                # 設定を一括で更新
                aircon_state.update_if_none(pmv_threshold.aircon_state)
                found_threshold = True  # 条件を満たすデータが見つかった
                break

        # 条件を満たすデータがなかった場合、最後の要素の設定を使用
        if not found_threshold and aircon_settings.pmv_threshold_settings.pmv_thresholds:
            last_threshold = aircon_settings.pmv_threshold_settings.pmv_thresholds[-1]
            aircon_state.update_if_none(last_threshold.aircon_state)

        return aircon_state

    # 特殊な条件下でのエアコンの設定の判断

    @staticmethod
    def _get_aircon_state_for_conditions(
        aircon_state: AirconState,
        pmv_result: PMVResult,
        home_sensor: HomeSensor,
        is_sleeping: bool,
    ) -> AirconState:
        """
        エアコンの設定を調整するメソッド。
        各種環境条件に基づいてエアコンの温度、モード、風量を変更する。
        Args:
            aircon_state (constants.AirconState): 現在のエアコン設定。
            pmv_result (PMVResult): PMV計算結果を持つオブジェクト。
            home_sensor (HomeSensor): 家庭の環境情報を格納したオブジェクト。
            is_sleeping (bool): 寝ている時間。
        Returns:
            constants.AirconState: 調整後のエアコン設定。
        """
        settings = GeneralSettings()
        aircon_settings = AirconSettings()

        # 冷却設定を短縮
        dew_point_control = aircon_settings.environmental_control_settings.dew_point_control
        cooling_stop_settings = dew_point_control.cooling_stop_settings
        cooling_settings = dew_point_control.cooling_settings
        cooling_activation_criteria = (
            aircon_settings.environmental_control_settings.cooling_activation_criteria
        )
        heating_activation_criteria = (
            aircon_settings.environmental_control_settings.heating_activation_criteria
        )
        dehumidification_settings = (
            aircon_settings.environmental_control_settings.dehumidification_settings
        )

        # 外気センサーがある場合のみ処理を実行
        if home_sensor.outdoor:
            # 冷房設定の場合の処理
            if aircon_state.mode in [
                constants.AirconMode.POWERFUL_COOLING,
                constants.AirconMode.COOLING,
            ]:
                if (
                    pmv_result.mean_radiant_temperature
                    - cooling_activation_criteria.outdoor_temperature_difference
                    > home_sensor.outdoor.air_quality.temperature
                    and pmv_result.pmv < cooling_activation_criteria.pmv_threshold
                ):
                    aircon_state.update_if_none(cooling_activation_criteria.aircon_state)
                    logger.info("外気温が低いので自然に温度が下がるのを待ちます。")

            # 暖房設定の場合の処理
            if aircon_state.mode in [
                constants.AirconMode.POWERFUL_HEATING,
                constants.AirconMode.HEATING,
            ]:
                if (
                    pmv_result.mean_radiant_temperature
                    - heating_activation_criteria.outdoor_temperature_difference
                    < home_sensor.outdoor.air_quality.temperature
                    and pmv_result.pmv > heating_activation_criteria.pmv_threshold
                ):
                    aircon_state.update_if_none(heating_activation_criteria.aircon_state)
                    logger.info("外気温が高いので自然に温度が上がるのを待ちます。")

        # 送風モードの場合の処理
        if aircon_state.mode == constants.AirconMode.FAN:
            if (
                home_sensor.average_indoor_absolute_humidity
                > settings.environment_settings.dehumidification_threshold
            ):
                logger.info(
                    "絶対湿度が閾値(%.1f)を超えました。",
                    settings.environment_settings.dehumidification_threshold,
                )
                aircon_state.update_if_none(dehumidification_settings.aircon_state)

        # リビング床温度と他の部屋の温度の差が1度以上の場合、風量をHIGHに設定
        # 気温差が最大の補助センサーを取得する
        max_diff_value = 0

        for supplementary in home_sensor.supplementaries:
            # メインセンサーと補助センサー間の気温差を計算
            diff = abs(
                home_sensor.main.air_quality.temperature - supplementary.air_quality.temperature
            )

            # 最大の気温差が見つかった場合、そのセンサーと差分を保存
            if diff > max_diff_value:
                max_diff_value = diff

        if (
            is_sleeping == False
            and max_diff_value
            > aircon_settings.environmental_control_settings.air_circulation_threshold
        ):
            logger.info(
                "リビングと他の部屋の温度の差が%s度以上です。温度差改善のため風量を上げます。",
                aircon_settings.environmental_control_settings.air_circulation_threshold,
            )
            aircon_state.fan_speed = constants.AirconFanSpeed.HIGH

        # 室内温度が露点温度より低い場合の処理
        if (
            home_sensor.main.air_quality.temperature
            < home_sensor.indoor_dew_point - dew_point_control.condensation_prevention_threshold
        ):
            if pmv_result.pmv > dew_point_control.pmv_threshold_for_cooling:
                logger.info("室内温度が露点温度より低いが、PMVが高い（%s）。", pmv_result.pmv)
                aircon_state.update_if_none(cooling_settings)
                aircon_state.force_fan_below_dew_point = True
            else:
                logger.info("室内温度が露点温度より低い。")
                aircon_state.update_if_none(cooling_stop_settings)
                aircon_state.force_fan_below_dew_point = True

        # CO2が高い場合、風量を上げる
        if home_sensor.main_co2_level > settings.co2_thresholds.warning_level_threshold:
            if aircon_state.fan_speed != constants.AirconFanSpeed.HIGH:
                aircon_state.fan_speed = constants.AirconFanSpeed.HIGH
        elif home_sensor.main_co2_level > settings.co2_thresholds.high_level_threshold:
            if aircon_state.fan_speed not in [
                constants.AirconFanSpeed.MEDIUM,
                constants.AirconFanSpeed.HIGH,
            ]:
                aircon_state.fan_speed = constants.AirconFanSpeed.MEDIUM

        # CO2テスト
        # if is_sleeping == True:
        #     aircon_state.fan_speed = constants.AirconFanSpeed.HIGH
        #     aircon_state.mode = constants.AirconMode.DRY

        return aircon_state  # 調整されたエアコン設定を返す
