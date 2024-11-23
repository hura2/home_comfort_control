from api.smart_devices.smart_device_factory import SmartDeviceFactory
from common import constants
from db.aircon_min_runtime_manager import AirconMinRuntimeManager
from db.analytics import Analytics
from logger.log_messages import LogMessages
from logger.system_event_logger import SystemEventLogger
from models.aircon_state import AirconState
from settings.general_settings import GeneralSettings
from util.time import TimeUtil


class AirconStateManager:
    """エアコンの状態を管理するクラス。"""

    # エアコンの設定を変更しても良いか判断
    @staticmethod
    def _can_change_aircon_state(mode: constants.AirconMode, max_temperature: float) -> bool:
        """指定されたモードと最高気温に基づいて、エアコンの設定変更が可能かどうかを判断する。

        Args:
            mode (constants.AirconMode): エアコンのモード。
            max_temperature (float): 最高気温。

        Returns:
            bool: 設定変更が可能であればTrue、そうでなければFalse。
        """
        latest_operation = AirconMinRuntimeManager.get_aircon_min_runtime_tracker_for_conditions(
            mode, max_temperature
        )

        if latest_operation is None:
            # 条件に合致する設定がない場合は変更可能
            return True

        duration_minutes, start_time = latest_operation

        # start_timeがNoneの場合は変更可能とする
        if start_time is None:
            return True

        # 設定が変更されてからの経過時間を確認
        elapsed_time = TimeUtil.get_current_time() - start_time
        elapsed_seconds = elapsed_time.total_seconds()

        if elapsed_seconds < duration_minutes * 60:
            # 最低経過時間前なのでモードを継続します
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            SystemEventLogger.log_info(
                LogMessages.MIN_RUNTIME_NOT_REACHED, hours=int(hours), minutes=int(minutes)
            )
            return False  # まだ継続時間内であるため変更不可

        SystemEventLogger.log_info(LogMessages.MIN_ELAPSED_TIME_REACHED)
        return True  # 継続時間が経過したため変更可能

    # エアコンの設定を変更
    @staticmethod
    def update_aircon_state(aircon_state: AirconState, current_aircon_state: AirconState = None):
        """エアコンの状態を更新し、設定をログに記録する。

        Args:
            aircon_state (AirconState): 更新するエアコンの状態。
        """
        # エアコンの設定をログに出力
        SystemEventLogger.log_aircon_state(aircon_state, current_aircon_state)
        smart_device = SmartDeviceFactory.create_device()
        smart_device.aircon(aircon_state)
        SystemEventLogger.log_info(LogMessages.AIRCON_SETTINGS_SUCCESS, aircon_state=SystemEventLogger.format_state(aircon_state))
        # 設定ファイル読み込み
        settings = GeneralSettings()
        if settings.database_settings.use_database:
            Analytics.insert_aircon_state(aircon_state)
