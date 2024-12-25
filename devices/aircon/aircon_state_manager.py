from api.smart_home_devices.smart_home_device_factory import SmartHomeDeviceFactory
from db.db_session_manager import DBSessionManager
from logger.system_event_logger import SystemEventLogger
from repository.services.aircon_change_intarval_service import AirconChangeIntarvalService
from shared.dataclass.aircon_settings import AirconSettings
from shared.enums.aircon_mode import AirconMode
from util.time_helper import TimeHelper


class AirconStateManager:
    """エアコンの状態を管理するクラス。"""

    # エアコンの設定を変更しても良いか判断
    @staticmethod
    def _can_change_aircon_settings(mode: AirconMode, max_temperature: float) -> bool:
        """指定されたモードと最高気温に基づいて、エアコンの設定変更が可能かどうかを判断する。

        Args:
            mode (AirconMode): エアコンのモード。
            max_temperature (float): 最高気温。

        Returns:
            bool: 設定変更が可能であればTrue、そうでなければFalse。
        """
        with DBSessionManager.session() as session:
            aircon_change_intarval = AirconChangeIntarvalService(session)
            duration_minutes, start_time = (
                aircon_change_intarval.get_aircon_min_runtime_tracker_for_conditions(
                    mode, max_temperature
                )
            )

        if duration_minutes is None:
            # 条件に合致する設定がない場合は変更可能
            return True

        # start_timeがNoneの場合は変更可能とする
        if start_time is None:
            return True

        # 設定が変更されてからの経過時間を確認
        elapsed_time = TimeHelper.get_current_time() - start_time
        elapsed_seconds = elapsed_time.total_seconds()

        if elapsed_seconds < duration_minutes * 60:
            # 最低経過時間前なのでモードを継続します
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            SystemEventLogger.log_info(
                "aircon_related.min_runtime_not_reached", hours=int(hours), minutes=int(minutes)
            )
            return False  # まだ継続時間内であるため変更不可

        SystemEventLogger.log_info("aircon_related.min_elapsed_time_reached")
        return True  # 継続時間が経過したため変更可能

    # エアコンの設定を変更
    @staticmethod
    def update_aircon_settings(
        aircon_settings: AirconSettings, current_aircon_settings: AirconSettings | None = None
    ) -> AirconSettings:
        """エアコンの状態を更新し、設定をログに記録する。

        Args:
            aircon_settings (AirconSettings): 更新するエアコンの状態。
        """
        # エアコンの設定をログに出力
        SystemEventLogger.log_aircon_settings(aircon_settings, current_aircon_settings)
        smart_device = SmartHomeDeviceFactory.create_device()
        smart_device.aircon(aircon_settings)
        SystemEventLogger.log_info(
            "aircon_related.aircon_settings_success",
            aircon_state=SystemEventLogger.format_settings(aircon_settings),
        )
        return aircon_settings
        # 設定ファイル読み込み
        # settings = GeneralConfig()
        # if settings.database_settings.use_database:
        # Analytics.insert_aircon_state(aircon_state)
