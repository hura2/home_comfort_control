
from api.notify.notify_factory import NotifyFactory
from api.smart_devices.smart_devise_exception import SmartDeviceException
from home_comfort_control import HomeComfortControl
from logger.system_event_logger import SystemEventLogger
from settings.general_settings import GeneralSettings
from util.clothing_activity_by_temperature import ClothingActivityByTemperature
from util.thermal_comfort import ThermalComfort
from util.time import TimeUtil


# メイン関数
def main():
    # 設定ファイル読み込み
    settings = GeneralSettings()
    # ホームコンフォートコントロールを初期化
    home_comfort_control = HomeComfortControl(settings)
    # 最高気温を取得（天気予報）
    forecast_max_temperature = home_comfort_control.fetch_forecast_max_temperature()
    # home_comfort_control.get_running_mean_temperature()
    # センサー情報を取得
    home_sensor = home_comfort_control.initialize_home_sensor()
    # outdoorセンサーの設定がある場合、外気温を設定。ない場合は、天気予報の最高気温を設定
    # outdoor_or_forecast_temperature = (
    #     home_sensor.outdoor.air_quality.temperature
    #     if home_sensor.outdoor
    #     else forecast_max_temperature
    # )
    # 現在時刻を取得
    now = TimeUtil.get_current_time()
    # 就寝中かどうかを判断（起動時間内ならばFalse,それ以外はTrue）
    is_sleeping = home_comfort_control.is_within_sleeping_period(now)
    # ログに環境情報を出力
    SystemEventLogger.log_environment_data(home_sensor, forecast_max_temperature, now)
    # METとICLの値を計算
    comfort_factors = ClothingActivityByTemperature.calculate_comfort_factors(
        home_sensor.outdoor.air_quality.temperature, forecast_max_temperature, is_sleeping
    )
    # PMV値を計算
    pmv_result = ThermalComfort.calculate_pmv(
        home_sensor, forecast_max_temperature, comfort_factors
    )
    # 高温条件の場合の、サーキュレーターの状態を取得
    circulator_state_heat_conditions = home_comfort_control.activate_circulator_in_heat_conditions(
        home_sensor, pmv_result.pmv, forecast_max_temperature
    )
    # サーキュレーターがオンになる場合、風量を増やしてPMV値を再計算
    pmv_result = (
        home_comfort_control.recalculate_pmv_with_circulator(
            home_sensor, forecast_max_temperature, circulator_state_heat_conditions, comfort_factors
        )
        or pmv_result
    )

    # 結果をログに出力
    SystemEventLogger.log_pmv(pmv_result, comfort_factors)
    # PMVを元にエアコンの設定を判断
    home_comfort_control.update_aircon_state(
        home_sensor, pmv_result, forecast_max_temperature, is_sleeping
    )
    # サーキュレーターの状態を更新
    circulator_state = home_comfort_control.update_circulator_state(
        home_sensor,
        circulator_state_heat_conditions,
        is_sleeping,
        home_sensor.outdoor.air_quality.temperature,
        forecast_max_temperature,
    )
    # データベースに記録
    home_comfort_control.record_environment_data(home_sensor, pmv_result, circulator_state, now)

    return True


# メイン関数を呼び出す
if __name__ == "__main__":
    try:
        main()
        SystemEventLogger.check_and_notify()
    except SmartDeviceException as sde:
        SystemEventLogger.log_exception(sde)
        NotifyFactory.create_manager().notify_important(f"スマートデバイス操作でエラーが発生しました。{sde}")
        exit(1)