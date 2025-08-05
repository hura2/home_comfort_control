import os
import traceback

from dotenv import load_dotenv

from api.notify.notify_factory import NotifyFactory
from api.smart_home_devices.smart_home_device_exception import SmartHomeDeviceException
from home_comfort_control import HomeComfortControl
from logger.system_event_logger import SystemEventLogger, logger
from shared.dataclass.effective_outdoor_temperature import EffectiveOutdoorTemperature
from translations.translated_value_error import TranslatedValueError
from util.met_clo_adjuster import MetCloAdjuster
from util.thermal_comfort import ThermalComfort


# メイン関数
def main():
    # ホームコンフォートコントロールを初期化
    home_comfort_control = HomeComfortControl()
    # 天気予報を取得してDBに保存
    home_comfort_control.fetch_forecast()
    # 本日の最高気温を取得
    forecast_max_temperature = home_comfort_control.fetch_forecast_max_temperature()
    # 現在時刻を基準に次の時間単位の天気予報を取得する
    closest_future_forecast = home_comfort_control.get_closest_future_forecast()
    # センサー情報を取得
    home_sensor = home_comfort_control.initialize_home_sensor()
    # 外気の基準となる温度を決める
    eff_temperature = EffectiveOutdoorTemperature(
        outdoor_temperature=(
            home_sensor.outdoor.air_quality.temperature if home_sensor.outdoor else None
        ),
        forecast_temperature=forecast_max_temperature,
    )
    # 就寝中かどうかを判断（起動時間内ならばFalse,それ以外はTrue）
    is_sleeping = home_comfort_control.is_within_sleeping_period()
    # ログに環境情報を出力
    SystemEventLogger.log_environment_data(home_sensor, eff_temperature.forecast_temperature, closest_future_forecast)
    # METとICLの値を計算
    comfort_factors = MetCloAdjuster.calculate_comfort_factors(
        eff_temperature,
        is_sleeping,
    )
    # PMV値を計算
    pmv_result = ThermalComfort.calculate_pmv(home_sensor, eff_temperature.value, comfort_factors)
    # 高温条件の場合の、サーキュレーターの状態を取得
    circulator_settings_heat_conditions = home_comfort_control.activate_circulator_in_heat_conditions(
        home_sensor, pmv_result.pmv, eff_temperature.value
    )
    # サーキュレーターがオンになる場合、風量を増やしてPMV値を再計算
    pmv_result = (
        home_comfort_control.recalculate_pmv_with_circulator(
            home_sensor, eff_temperature.value, circulator_settings_heat_conditions, comfort_factors
        )
        or pmv_result
    )

    # 結果をログに出力
    SystemEventLogger.log_pmv(pmv_result, comfort_factors)

    # PMVを元にエアコンの設定を判断
    aircon_settings = home_comfort_control.update_aircon_settings(
        home_sensor, pmv_result, eff_temperature.value, is_sleeping
    )
    # サーキュレーターの状態を更新
    circulator_settings = home_comfort_control.update_circulator_settings(
        home_sensor,
        circulator_settings_heat_conditions,
        is_sleeping,
        eff_temperature.value,
    )
    # データベースに記録
    home_comfort_control.record_environment_data(
        home_sensor, pmv_result, aircon_settings, circulator_settings
    )

    return True


# メイン関数を呼び出す
if __name__ == "__main__":
    # 環境変数の読み込み
    # 明示的に環境変数をクリア
    # os.environ.clear()
    # load_dotenv(".env", override=True)
    try:
        main()
        notify_manager = NotifyFactory.create_manager()
        # エラーが発生した場合は重要通知を送る
        if SystemEventLogger.check_error():
            notify_manager.notify_important(SystemEventLogger.get_buffered_logs())
        # 通常通知を送る
        notify_manager.notify_normal(SystemEventLogger.get_buffered_logs())
    except SmartHomeDeviceException as sde:
        SystemEventLogger.log_exception(sde)
        NotifyFactory.create_manager().notify_important(
            f"スマートホームデバイス操作でエラーが発生しました。{sde}"
        )
        logger.error(traceback.format_exc())
        exit(1)
    except TranslatedValueError as tve:
        SystemEventLogger.log_exception(tve)
        logger.error(traceback.format_exc())
        exit(1)
