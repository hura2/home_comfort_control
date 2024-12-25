import i18n
import pytz
from pydantic import ValidationError

from preferences.aircon.aircon_preference import AirconPreference
from preferences.app.app_preference import AppPreference
from preferences.circulator.circulator_preference import CirculatorPreference
from preferences.met_clo.met_clo_preference import MetCloPreference
from preferences.thermal.thermal_preference import ThermalPreference
from preferences.yaml_loader import YamlLoader
from translations.translated_pydantic_value_error import TranslatedPydanticValueError
from util.string_helper import StringHelper

# 日本時間を設定
LOCAL_TZ = pytz.timezone("Asia/Tokyo")

i18n.set("file_format", "yaml")
i18n.load_path.append("./translations")
i18n.set("locale", "ja")

# app_config = AppConfig()
try:
    app_preference = AppPreference(**YamlLoader.load_config("app_preference.yaml"))
    aircon_preference = AirconPreference(**YamlLoader.load_config("aircon_preference.yaml"))
    circulator_preference = CirculatorPreference(
        **YamlLoader.load_config("circulator_preference.yaml")
    )
    met_clo_preference = MetCloPreference(**YamlLoader.load_config("met_clo_preference.yaml"))
    thermal_preference = ThermalPreference(**YamlLoader.load_config("thermal_preference.yaml"))
except ValidationError as e:
    # エラー情報を処理してユーザーにわかりやすいメッセージを生成
    error_messages = []

    for error in e.errors():
        loc = " -> ".join(str(loc) for loc in error["loc"])  # エラー箇所を表示
        msg = error["msg"]  # エラーメッセージ
        ctx = error.get("ctx", {})  # コンテキスト（例: 範囲外エラーの閾値情報など）

        # print(ctx, msg)
        # コンテキストがある場合
        if ctx:
            # ge と le を同時に含む場合
            if "ge" in ctx and "le" in ctx:
                details = i18n.t("validation_error.details.ge_le", ge=ctx["ge"], le=ctx["le"])
            # ge のみ
            elif "ge" in ctx:
                details = i18n.t("validation_error.details.ge", ge=ctx["ge"])
            # le のみ
            elif "le" in ctx:
                details = i18n.t("validation_error.details.le", le=ctx["le"])
            else:
                if isinstance(ctx["error"], TranslatedPydanticValueError):
                    tve: TranslatedPydanticValueError = ctx["error"]
                    # loc += " -> " + str(tve.property_name)
                    details = i18n.t(
                        f"validation_error.custom_message.{tve.message_key}", **tve.context
                    )
                else:
                    details = str(ctx["error"])
        else:
            # msg を翻訳ファイルで検索
            details = i18n.t(
                f"validation_error.message_map.{msg}",
                default=i18n.t("validation_error.default_message"),
            )

        # メッセージを追加
        location = i18n.t("validation_error.location", location=loc)
        error_messages.append(f"{location} {details}")

    # ユーザーにエラーメッセージを表示
    user_friendly_message = "\n".join(error_messages)
    print(
        i18n.t("validation_error.message")
        + f": {StringHelper.camel_to_snake(e.title)}.yaml\n"
        + user_friendly_message
    )
    exit(1)

except Exception as e:
    print(e)
