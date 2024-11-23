class LogMessages:
    # 時刻関連
    CURRENT_TIME = "現在時刻: {current_time}"
    FORECAST_MAX_TEMP = "最高気温予報: {forecast_max_temperature}°"

    # 環境データ
    CO2_LEVEL = "CO2濃度: {co2_level}ppm"
    SENSOR_DATA = "{label}:{location}: 温度{temperature:.1f}°, 湿度{humidity:.1f}%, 絶対湿度{absolute_humidity:.2f}g/㎥"
    TEMP_DIFF = "{reference_label}:{reference_location}との温度差{temp_diff:.1f}°"
    CO2_SENSOR = "CO2: {co2_level}ppm"

    # ICL調整関連
    ICL_ADJUSTMENT_HIGH_COST = "高コスト時間帯のICL調整を行いました: {start_time} - {end_time}"
    ICL_ADJUSTMENT_LOW_COST = "低コスト時間帯のICL調整を行いました: {start_time} - {end_time}"

    # PMV計算
    SURFACE_TEMPERATURES = (
        "表面温度:壁 {wall:.1f}°, 天井 {ceiling:.1f}°, 床 {floor:.1f}°, 平均放射温度: {mrt:.1f}°"
    )
    SENSIBLE_TEMP = "体感温度: {sensible_temperature:.1f}°"
    MET_ICL_VALUES = "met: {met:.1f}, icl: {icl:.1f}"
    RELATIVE_AIR_SPEED = "相対風速: {relative_air_speed:.1f}m/s"
    DYNAMIC_CLOTHING = "動的な衣服の断熱性: {dynamic_clothing_insulation:.1f}"
    PMV_PPD = "pmv = {pmv:.1f}, ppd = {ppd:.1f}%"

    # エアコン関連
    ELAPSED_TIME = "前回のエアコン設定からの経過: {hours}時間{minutes}分"
    AIRCON_STATE_CHANGE = "{current_state}から{new_state}に変更"
    AIRCON_STATE_INIT = "{new_state}に変更"
    AIRCON_SCORES = (
        "先々週のスコア平均: {week_before_last_score}\n"
        "先週のスコア平均: {last_week_score}\n"
        "今週のスコア平均: {this_week_score}\n"
        "昨日のスコア: {yesterday_score}\n"
        "今日のスコア予想: {today_score}"  # 改行を挿入
    )
    AIRCON_SETTINGS_SUCCESS = "エアコンの設定を送信しました: {aircon_state}"
    AIRCON_SETTINGS_FAILED = (
        "エアコンの設定を送信できませんでした。エラーメッセージ: {error_message}"
    )
    AIRCON_SETTINGS_RETRY = "別の方法で再送信を試みます"
    MIN_RUNTIME_NOT_REACHED = (
        "最低経過時間前なのでモードを継続します。経過時間:{hours}時間{minutes}分"
    )
    MIN_ELAPSED_TIME_REACHED = "最低経過時間を経過したので、設定を変更可能です。"
    SAME_MODE = "現在のモードと新しいモードが同じ: {current_mode}"
    DIFFERENT_MODE = (
        "現在のモードと新しいモードが違う: 現在のモード={current_mode}, 新しいモード={new_mode}"
    )
    COOLING_TO_COOLING = "現在モードが冷房モード、新しいモードも冷房モード"
    COOLING_TO_OTHER = "現在モードが冷房モード、新しいモードが冷房モード以外"
    HEATING_TO_HEATING = "現在モードが暖房モード、新しいモードも暖房モード"
    HEATING_TO_OTHER = "現在モードが暖房モード、新しいモードが暖房モード以外"
    AIRCON_MODE_CONTINUE_AND_UPDATE = "現在のモードを継続しつつ、設定を変更します"
    NON_COOLING_OR_HEATING = "現在モードが冷房でも暖房でもない場合: {current_mode}"
    INDOOR_TEMP_BELOW_DEWPOINT = "室内温度が露点温度より低い。"
    INDOOR_TEMP_BELOW_DEWPOINT_HIGH_PMV = "室内温度が露点温度より低いが、PMVが高い（{pmv}）。"
    ROOM_TEMP_DIFF_HIGH = (
        "リビングと他の部屋の温度の差が{temp_diff:.1f}度以上です。温度差改善のため風量を上げます。"
    )

    # 湿度関連
    ABSOLUTE_HUMIDITY_THRESHOLD_EXCEEDED = "絶対湿度が閾値({threshold:.1f})を超えました。"

    # 外気温関連
    WAIT_FOR_NATURAL_COOLING = "外気温が高いので自然に温度が上がるのを待ちます。"
    WAIT_FOR_NATURAL_HEATING = "外気温が低いので自然に温度が下がるのを待ちます。"

    # サーキュレーター関連
    CIRCULATOR_STATUS = "現在のサーキュレーターの電源: {power}, 風量: {fan_speed}"
    CIRCULATOR_UPDATE_FAN_SPEED = "サーキュレーターの風量を{new_fan_speed}に設定"
    CIRCULATOR_SETTINGS_SUCCESS = "サーキュレーターの設定を送信しました。電源: {power}, 風量: {fan_speed}"

    CIRCULATOR_OFF_NOTIFY = "サーキュレーターの電源をOFFに設定"
    CIRCULATOR_ON_NOTIFY = "サーキュレーターの風量を{new_fan_speed}に設定"

    # 例外関連
    EXCEPTION_OCCURRED = "例外発生: {exception}"
