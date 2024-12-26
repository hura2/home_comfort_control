from devices.aircon.aircon_state_manager import AirconStateManager
from logger.system_event_logger import SystemEventLogger
from settings import aircon_preference
from shared.dataclass.aircon_settings import AirconSettings
from shared.enums.aircon_fan_speed import AirconFanSpeed


class AirconOperation:
    """エアコンの操作を行うクラス。"""

    # エアコンの設定を必要に応じて更新
    @staticmethod
    def update_aircon_if_necessary(
        aircon_settings: AirconSettings,
        current_aircon_settings: AirconSettings,
        forecast_max_temperature: float,
    ) -> bool:
        """エアコンの設定を必要に応じて更新する。

        Args:
            aircon_settings (AirconSettings): 更新するエアコンの新しい状態。
            current_aircon_settings (AirconSettings): 現在のエアコンの状態。
            forecast_max_temperature (float): 現在の最高気温。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 強制送風のフラグが有効なら、設定を送風に変更
        if aircon_settings.force_fan_below_dew_point:
            AirconStateManager.update_aircon_settings(aircon_settings, current_aircon_settings)
            return True

        # 最低限の経過時間が確保されているかを確認し、可能であればエアコン設定を更新
        if not AirconStateManager._can_change_aircon_settings(
            current_aircon_settings.mode, forecast_max_temperature
        ):
            # 同一モードの場合や微調整の処理を実施
            return AirconOperation._handle_same_mode_or_adjust(
                aircon_settings, current_aircon_settings
            )

        # 設定を更新してTrueを返す
        AirconStateManager.update_aircon_settings(aircon_settings, current_aircon_settings)
        return True

    # エアコンが同一モードの場合やモード切り替えが必要な場合の処理
    @staticmethod
    def _handle_same_mode_or_adjust(
        aircon_settings: AirconSettings,
        current_aircon_settings: AirconSettings,
    ) -> bool:
        """エアコンの同一モードを維持するか、新しいモードに調整する処理を行う。

        Args:
            aircon_settings (AirconSettings): 新しいエアコンの状態。
            current_aircon_settings (AirconSettings): 現在のエアコンの状態。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 現在のエアコンモードに基づき処理を振り分け
        new_mode = aircon_settings.mode
        current_mode = current_aircon_settings.mode

        # 現在のモードと新しいモードが同じ場合の処理
        if new_mode == current_mode:
            SystemEventLogger.log_info("aircon_related.same_mode", current_mode=current_mode.label)
            return AirconOperation._update_if_settings_differ(
                aircon_settings, current_aircon_settings
            )
        else:
            SystemEventLogger.log_info(
                "aircon_related.different_mode", current_mode=current_mode, new_mode=new_mode
            )
            if current_mode.is_cooling():
                SystemEventLogger.log_info("aircon_related.cooling_to_cooling")
                if new_mode.is_cooling():
                    AirconStateManager.update_aircon_settings(
                        aircon_settings, current_aircon_settings
                    )
                    return True
                else:
                    SystemEventLogger.log_info("aircon_related.cooling_to_other")
                    AirconOperation._apply_weakest_setting(aircon_settings, current_aircon_settings)
                    return True

            if current_mode.is_heating():
                SystemEventLogger.log_info("aircon_related.heating_to_heating")
                if new_mode.is_heating():
                    AirconStateManager.update_aircon_settings(
                        aircon_settings, current_aircon_settings
                    )
                    return True
                else:
                    SystemEventLogger.log_info("aircon_related.heating_to_other")
                    AirconOperation._apply_weakest_setting(aircon_settings, current_aircon_settings)
                    return True

            SystemEventLogger.log_info(
                "aircon_related.non_cooling_or_heating", current_mode=current_mode
            )
            aircon_settings.mode = current_aircon_settings.mode
            AirconOperation._update_if_settings_differ(aircon_settings, current_aircon_settings)
            return False  # 同一モードなので設定を更新するが、モードは変更しない

    # 冷房モードでの最弱設定を適用
    @staticmethod
    def _apply_weakest_setting(
        aircon_settings: AirconSettings, current_aircon_settings: AirconSettings
    ):
        """エアコンの設定を最弱状態に適用する。

        Args:
            aircon_settings (AirconSettings): エアコンの新しい状態。
            current_aircon_settings (AirconSettings): 現在のエアコンの状態。
        """
        # 最弱設定をエアコン設定に適用
        if current_aircon_settings.mode.is_cooling():
            weakest_settings = aircon_preference.aircon_settings.weakest_cooling
        else:
            weakest_settings = aircon_preference.aircon_settings.weakest_heating

        # 温度、モード、ファン速度を最弱設定に変更
        aircon_settings.temperature = weakest_settings.aircon_settings.temperature
        aircon_settings.mode = weakest_settings.aircon_settings.mode
        if aircon_settings.fan_speed not in [
            AirconFanSpeed.MEDIUM,
            AirconFanSpeed.HIGH,
        ]:
            aircon_settings.fan_speed = weakest_settings.aircon_settings.fan_speed

        # 最弱設定を適用
        AirconStateManager.update_aircon_settings(aircon_settings, current_aircon_settings)

    # 現在の設定と異なる場合にエアコン設定を更新
    @staticmethod
    def _update_if_settings_differ(
        aircon_settings: AirconSettings,
        current_aircon_settings: AirconSettings,
    ) -> bool:
        """エアコンの現在の設定が異なる場合、設定を更新する。

        Args:
            aircon_settings (AirconSettings): 新しいエアコンの状態。
            current_aircon_settings (AirconSettings): 現在のエアコンの状態。

        Returns:
            bool: 設定が変更された場合はTrue、そうでない場合はFalse。
        """
        # 温度、ファン速度、電源設定のいずれかが異なる場合、設定を更新
        if (
            current_aircon_settings.temperature != aircon_settings.temperature
            or current_aircon_settings.fan_speed.id != aircon_settings.fan_speed.id
            or current_aircon_settings.power.id != aircon_settings.power.id
        ):
            SystemEventLogger.log_info("aircon_related.mode_continue_and_update")

        AirconStateManager.update_aircon_settings(aircon_settings, current_aircon_settings)
        return False
