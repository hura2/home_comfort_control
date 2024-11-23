from common import constants
from devices.aircon.aircon_state_manager import AirconStateManager
from logger.log_messages import LogMessages
from logger.system_event_logger import SystemEventLogger
from models.aircon_state import AirconState
from settings.aircon_settings import AirconSettings


class AirconOperation:
    """エアコンの操作を行うクラス。"""

    # エアコンの設定を必要に応じて更新
    @staticmethod
    def update_aircon_if_necessary(
        aircon_state: AirconState,
        current_aircon_state: AirconState,
        forecast_max_temperature: float,
    ) -> bool:
        """エアコンの設定を必要に応じて更新する。

        Args:
            aircon_state (AirconState): 更新するエアコンの新しい状態。
            current_aircon_state (AirconState): 現在のエアコンの状態。
            forecast_max_temperature (float): 現在の最高気温。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 強制送風のフラグが有効なら、設定を送風に変更
        if aircon_state.force_fan_below_dew_point:
            AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
            return True

        # 最低限の経過時間が確保されているかを確認し、可能であればエアコン設定を更新
        if not AirconStateManager._can_change_aircon_state(
            current_aircon_state.mode, forecast_max_temperature
        ):
            # 同一モードの場合や微調整の処理を実施
            return AirconOperation._handle_same_mode_or_adjust(aircon_state, current_aircon_state)

        # 設定を更新してTrueを返す
        AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
        return True

    # エアコンが同一モードの場合やモード切り替えが必要な場合の処理
    @staticmethod
    def _handle_same_mode_or_adjust(
        aircon_state: AirconState,
        current_aircon_state: AirconState,
    ) -> bool:
        """エアコンの同一モードを維持するか、新しいモードに調整する処理を行う。

        Args:
            aircon_state (AirconState): 新しいエアコンの状態。
            current_aircon_state (AirconState): 現在のエアコンの状態。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 現在のエアコンモードに基づき処理を振り分け
        new_mode = aircon_state.mode
        current_mode = current_aircon_state.mode

        # 現在のモードと新しいモードが同じ場合の処理
        if new_mode == current_mode:
            SystemEventLogger.log_info(LogMessages.SAME_MODE, current_mode=current_mode.description)
            return AirconOperation._update_if_settings_differ(aircon_state, current_aircon_state)
        else:
            SystemEventLogger.log_info(
                LogMessages.DIFFERENT_MODE, current_mode=current_mode, new_mode=new_mode
            )
            if constants.AirconMode.is_cooling_mode(current_mode):
                SystemEventLogger.log_info(LogMessages.COOLING_TO_COOLING)
                if constants.AirconMode.is_cooling_mode(new_mode):
                    return AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
                else:
                    SystemEventLogger.log_info(LogMessages.COOLING_TO_OTHER)
                    return AirconOperation._apply_weakest_setting(
                        aircon_state, current_aircon_state
                    )

            if constants.AirconMode.is_heating_mode(current_mode):
                SystemEventLogger.log_info(LogMessages.HEATING_TO_HEATING)
                if constants.AirconMode.is_heating_mode(new_mode):
                    return AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
                else:
                    SystemEventLogger.log_info(LogMessages.HEATING_TO_OTHER)
                    return AirconOperation._apply_weakest_setting(
                        aircon_state, current_aircon_state
                    )

            SystemEventLogger.log_info(LogMessages.NON_COOLING_OR_HEATING, current_mode=current_mode)
            aircon_state.mode = current_aircon_state.mode
            AirconOperation._update_if_settings_differ(aircon_state, current_aircon_state)
            return False  # 同一モードなので設定を更新するが、モードは変更しない


    # 冷房モードでの最弱設定を適用
    @staticmethod
    def _apply_weakest_setting(aircon_state: AirconState, current_aircon_state: AirconState):
        """エアコンの設定を最弱状態に適用する。

        Args:
            aircon_state (AirconState): エアコンの新しい状態。
            current_aircon_state (AirconState): 現在のエアコンの状態。
        """
        # 最弱設定をエアコン設定に適用
        aircon_settings = AirconSettings()
        if constants.AirconMode.is_cooling_mode(current_aircon_state.mode):
            weakest_state = aircon_settings.weakest_aircon_settings.cooling_settings
        else:
            weakest_state = aircon_settings.weakest_aircon_settings.heating_settings

        # 温度、モード、ファン速度を最弱設定に変更
        aircon_state.temperature = weakest_state.temperature
        aircon_state.mode = weakest_state.mode
        if aircon_state.fan_speed not in [
            constants.AirconFanSpeed.MEDIUM,
            constants.AirconFanSpeed.HIGH,
        ]:
            aircon_state.fan_speed = weakest_state.fan_speed

        # 最弱設定を適用
        AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)

    # 現在の設定と異なる場合にエアコン設定を更新
    @staticmethod
    def _update_if_settings_differ(
        aircon_state: AirconState,
        current_aircon_state: AirconState,
    ) -> bool:
        """エアコンの現在の設定が異なる場合、設定を更新する。

        Args:
            aircon_state (AirconState): 新しいエアコンの状態。
            current_aircon_state (AirconState): 現在のエアコンの状態。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 温度、ファン速度、電源設定のいずれかが異なる場合、設定を更新
        if (
            current_aircon_state.temperature != aircon_state.temperature
            or current_aircon_state.fan_speed.id != aircon_state.fan_speed.id
            or current_aircon_state.power.id != aircon_state.power.id
        ):
            SystemEventLogger.log_info(LogMessages.AIRCON_MODE_CONTINUE_AND_UPDATE)
            # AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
            # return False  # 設定が異なるため更新を行った

        # LoggerUtil.log_aircon_state(aircon_state, current_aircon_state)
        AirconStateManager.update_aircon_state(aircon_state, current_aircon_state)
        return False 
