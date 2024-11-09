import datetime
from typing import Optional, Tuple

import common.constants as constants
from db.supabase_client import SupabaseClient
from util.time import TimeUtil


class AirconMinRuntimeManager:
    """
    エアコンの設定を管理するクラス。

    このクラスは、エアコンの運転時間に関する情報を管理し、データベースから必要な情報を取得したり、更新したりする機能を提供します。
    """

    @staticmethod
    def get_aircon_min_runtime_tracker_for_conditions(
        mode: constants.AirconMode, max_temperature: float
    ) -> Optional[Tuple[int, datetime.datetime]]:
        """
        指定されたエアコンモードと最高気温に基づいて、最小運転時間トラッカーの情報を取得します。

        Args:
            mode (AirconMode): 取得したいエアコンの運転モード。
            max_temperature (float): 対象となる最高気温。

        Returns:
            Optional[Tuple[int, datetime.datetime]]: 最小運転時間（分）と開始時刻のタプル。
            該当するデータが存在しない場合は None を返します。
        """
        data = (
            SupabaseClient.get_supabase()
            .table("aircon_min_runtime_trackers")
            .select("duration_minutes, start_time")
            .eq("mode", AirconMinRuntimeManager._convert_powerful_mode(mode).id)  # モードでフィルタリング
            .lte("temperature_min", max_temperature)  # 最高気温以下
            .gte("temperature_max", max_temperature)  # 最高気温以上
            .order("temperature_min", desc=True)  # 温度の条件に基づいて優先
            .limit(1)
            .execute()
        )

        if not data.data:
            return None

        latest_operation = data.data[0]
        duration_minutes = latest_operation["duration_minutes"]  # 最小運転時間を取得
        start_time = TimeUtil.parse_datetime_string(latest_operation["start_time"])  # 開始時刻を解析
        return duration_minutes, start_time

    @staticmethod
    def update_start_time_if_exists(mode: constants.AirconMode, forecast_max_temperature: float) -> None:
        """
        aircon_min_runtime_trackersテーブルの既存の操作の開始時刻を更新します。
        max_temperatureがtemperature_maxとtemperature_minの間に一致するレコードが存在する場合のみ更新します。

        Args:
            mode (AirconMode): 更新対象のエアコンモード。
            forecast_max_temperature (float): 比較対象の最高気温。

        Returns:
            None
        """
        AirconMinRuntimeManager.reset_all_start_times()  # すべての開始時刻をリセット
        # Supabaseのクライアントを取得
        supabase_client = SupabaseClient.get_supabase()

        # max_temperatureがtemperature_maxとtemperature_minの間にある既存レコードを取得
        existing_record = (
            supabase_client.table("aircon_min_runtime_trackers")
            .select("*")
            .eq("mode", AirconMinRuntimeManager._convert_powerful_mode(mode).id)  # モードでフィルタリング
            .gte("temperature_max", forecast_max_temperature)  # temperature_max以上
            .lte("temperature_min", forecast_max_temperature)  # temperature_min以下
            .execute()
        )

        # レコードが存在する場合に開始時刻を更新
        if existing_record.data:
            record_id = existing_record.data[0]["id"]  # レコードのIDを取得
            supabase_client.table("aircon_min_runtime_trackers").update(
                {"start_time": TimeUtil.get_current_time().isoformat()}  # ISOフォーマットで現在時刻を設定
            ).eq(
                "id", record_id  # レコードIDでフィルタリング
            ).execute()  # 更新を実行

    @staticmethod
    def reset_all_start_times() -> None:
        """
        aircon_min_runtime_trackersテーブル内の全レコードのstart_timeをNULLにリセットします。

        Returns:
            None
        """
        # 全件のstart_timeをNULLにリセット
        result = (
            SupabaseClient.get_supabase()
            .table("aircon_min_runtime_trackers")
            .update({"start_time": None})  # NULL値を設定
            .neq("start_time", "1970-01-01T00:00:00Z")
            .execute()
        )  # 特定の値を持つレコードは除外

    @staticmethod
    def _convert_powerful_mode(mode: constants.AirconMode) -> constants.AirconMode:
        """
        パワフルモードを通常のモードに変換します。

        Args:
            mode (AirconMode): 変換対象のエアコンモード。

        Returns:
            AirconMode: 変換後のエアコンモード。
        """
        # パワフルクーリングを通常のクーリングに変換
        if mode == constants.AirconMode.POWERFUL_COOLING:
            return constants.AirconMode.COOLING

        # パワフルヒーティングを通常のヒーティングに変換
        if mode == constants.AirconMode.POWERFUL_HEATING:
            return constants.AirconMode.HEATING

        return mode  # 変換不要な場合はそのまま返す
