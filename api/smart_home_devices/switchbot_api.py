import base64
import hashlib
import hmac
import json
import os
import time
from typing import Dict

import requests

from api.smart_home_devices.smart_home_device_exception import SmartHomeDeviceException
from api.smart_home_devices.smart_home_device_interface import SmartHomeDeviceInterface
from api.smart_home_devices.smart_home_device_response import SmartHomeDeviceResponse
from logger.system_event_logger import SystemEventLogger
from shared.dataclass.air_quality import AirQuality
from shared.dataclass.aircon_settings import AirconSettings
from shared.dataclass.sensor import Sensor
from shared.enums.aircon_mode import AirconMode
from shared.enums.circulator_fan_speed import CirculatorFanSpeed
from shared.enums.power_mode import PowerMode
from shared.enums.sensor_type import SensorType
from translations.translated_value_error import TranslatedValueError
from util.env_config_loader import EnvConfigLoader


class SwitchBotApi(SmartHomeDeviceInterface):
    def __init__(self):
        super().__init__()

        # 環境変数から読み込んだアクセストークンやデバイスIDを格納するクラス変数
        self._ACCESS_TOKEN = EnvConfigLoader.get_variable("SWITCHBOT_ACCESS_TOKEN")
        self._SECRET = EnvConfigLoader.get_variable("SWITCHBOT_SECRET")
        self._CIRCULATOR_DEVICE_ID = EnvConfigLoader.get_variable("SWITCHBOT_CIRCULATOR_DEVICE_ID")
        self._AIR_CONDITIONER_DEVICE_ID = EnvConfigLoader.get_variable(
            "SWITCHBOT_AIR_CONDITIONER_DEVICE_ID"
        )
        self._AIR_CONDITIONER_SUPPORT_DEVICE_ID = EnvConfigLoader.get_variable(
            "SWITCHBOT_AIR_CONDITIONER_SUPPORT_DEVICE_ID"
        )

        # APIのベースURL
        self._API_BASE_URL = EnvConfigLoader.get_variable("SWITCHBOT_BASE_URL")

    def circulator_on(self) -> SmartHomeDeviceResponse:
        """サーキュレーターをオンにする"""
        try:
            return self._post_command(
                self._CIRCULATOR_DEVICE_ID,
                PowerMode.ON.id,
                "default",
                "customize",
            )
        except SmartHomeDeviceException as e:
            raise SmartHomeDeviceException(e.message, e.send_command, "circulator")

    def circulator_off(self) -> SmartHomeDeviceResponse:
        """サーキュレーターをoffにする"""
        try:
            return self._post_command(
                self._CIRCULATOR_DEVICE_ID,
                PowerMode.OFF.id,
                "default",
                "customize",
            )
        except SmartHomeDeviceException as e:
            raise SmartHomeDeviceException(e.message, e.send_command, "circulator")

    def circulator_fan_speed(
        self, speed: int, current_speed: int | None = None
    ) -> SmartHomeDeviceResponse | None:
        try:
            adjust_speed: int = current_speed or 0
            response = None
            while adjust_speed != speed:
                if speed > adjust_speed:
                    response = self._increase_circulator_volume()
                    if response.success == False:
                        return response
                    # ファンスピードを増加させる
                    adjust_speed += 1
                else:
                    response = self._decrease_circulator_volume()  # ファンスピードを減少させる
                    if response.success == False:
                        return response
                    adjust_speed -= 1
            return response
        except SmartHomeDeviceException as e:
            raise SmartHomeDeviceException(e.message, e.send_command, "circulator_fan_speed")

    def get_air_quality_by_sensor(self, sensor: Sensor) -> AirQuality:
        # 位置に応じたデバイスIDを取得
        device_id_key = f"SWITCHBOT_{sensor.id.upper()}_DEVICE_ID"
        device_id = os.getenv(device_id_key)
        if not device_id:
            raise TranslatedValueError(device_id_key=device_id_key)

        try:
            if sensor.type == SensorType.TEMPERATURE_HUMIDITY:
                # 温湿度データを取得
                return self._get_temperature_and_humidity(device_id)
            else:
                # sensor.type == SensorType.CO2:
                # CO2データを取得
                return self._get_co2_sensor_data(device_id)
        except SmartHomeDeviceException as e:
            raise SmartHomeDeviceException(e.message, e.send_command, sensor.label)

    def aircon(self, aircon_settings: AirconSettings) -> SmartHomeDeviceResponse:
        try:
            if aircon_settings.mode.id == AirconMode.POWERFUL_COOLING.id:
                # パワフルモードは通常のエアコン設定では行えないため、別のデバイスIDで送信する
                return self._post_command(
                    self._AIR_CONDITIONER_SUPPORT_DEVICE_ID,
                    AirconMode.POWERFUL_COOLING.label,
                    "default",
                    "customize",
                )

            if aircon_settings.mode.id == AirconMode.POWERFUL_HEATING.id:
                # パワフルモードは通常のエアコン設定では行えないため、別のデバイスIDで送信する
                return self._post_command(
                    self._AIR_CONDITIONER_SUPPORT_DEVICE_ID,
                    AirconMode.POWERFUL_HEATING.label,
                    "default",
                    "customize",
                )

            try:
                res = self._post_command(
                    self._AIR_CONDITIONER_DEVICE_ID,
                    "setAll",
                    f"{aircon_settings.temperature},{aircon_settings.mode.id},{aircon_settings.fan_speed.id},{aircon_settings.power.id}",
                    "command",
                )
                return res
            except SmartHomeDeviceException as e:
                SystemEventLogger.log_error(class_type=self.__class__, message=str(e))
                SystemEventLogger.log_info("aircon_related.aircon_settings_retry")
                return self._post_command(
                    self._AIR_CONDITIONER_SUPPORT_DEVICE_ID,
                    aircon_settings.mode.label,
                    "default",
                    "customize",
                )
        except SmartHomeDeviceException as e:
            raise SmartHomeDeviceException(e.message, e.send_command, "aircon")

    def _post_command(
        self,
        device_id: str,
        command: str,
        parameter: str = "default",
        command_type: str = "command",
    ) -> SmartHomeDeviceResponse:
        """
        指定したデバイスにコマンドを送信し、その結果を取得します。

        Args:
            device_id (str): デバイスID
            command (str): 送信するコマンド
            parameter (str): コマンドのパラメータ（デフォルトは"default"）
            command_type (str): コマンドの種類（デフォルトは"command"）

        Returns:
            SmartDeviceResponse: コマンドの実行結果
        """
        url = f"{self._API_BASE_URL}/v1.1/devices/{device_id}/commands"
        body = {"command": command, "parameter": parameter, "commandType": command_type}
        data = json.dumps(body)
        try:
            # コマンド送信前に一時停止（例: 2秒待つ）
            time.sleep(2)
            with requests.Session() as session:
                response = session.post(url, data=data, headers=self._generate_swt_header())
                response.raise_for_status()  # HTTPエラーがあれば例外を発生
                data = response.json()
                if data["statusCode"] == 100:
                    return SmartHomeDeviceResponse(message=data)
                else:
                    # 置換処理
                    url_with_masked_device_id = url.replace(f"{device_id}", "XXXXX")
                    raise SmartHomeDeviceException(
                        data["message"],
                        f"url: {url_with_masked_device_id}, body: {body}, data: {data}",
                    )
        except requests.exceptions.RequestException as e:
            raise SmartHomeDeviceException(str(e))

    def _get_temperature_and_humidity(self, device_id: str) -> AirQuality:
        """
        指定したデバイスの温度と湿度を取得し、AirQualityオブジェクトを返します。

        Args:
            device_id (str): デバイスID

        Returns:
            AirQuality: 温度と湿度を格納したAirQualityオブジェクト
        """
        data = self._fetch_device_data(device_id, 3, 5)
        return self._parse_air_quality(data)

    def _get_co2_sensor_data(self, device_id: str) -> AirQuality:
        """
        指定したCO2センサーの温度、湿度、CO2を取得し、AirQualityオブジェクトを返します。

        Args:
            device_id (str): デバイスID

        Returns:
            AirQuality: 温度、湿度、CO2を格納したAirQualityオブジェクト
        """
        data = self._fetch_device_data(device_id, retry_count=3, retry_delay=5)
        return self._parse_co2_sensor_data(data)

    def _fetch_device_data(self, device_id: str, retry_count: int, retry_delay: int) -> dict:
        """
        指定したデバイスのデータを取得し、辞書形式で返す。

        Args:
            device_id (str): デバイスID
            retry_count (int): リトライの試行回数
            retry_delay (int): リトライ間の遅延（秒）

        Returns:
            SmartDeviceResponse[dict]: デバイスのデータ
        """
        url = f"{self._API_BASE_URL}/v1.1/devices/{device_id}/status"
        error_message = ""

        for _ in range(retry_count):
            try:
                with requests.Session() as session:
                    response = session.get(url, headers=self._generate_swt_header())
                    response.raise_for_status()  # HTTPエラーがあれば例外を発生
                    data = response.json()
                    if data["statusCode"] == 100:
                        return data["body"]
                    else:
                        error_message = data["message"]
            except requests.exceptions.RequestException as e:
                time.sleep(retry_delay)

        # 置換処理
        url_with_masked_device_id = url.replace(f"{device_id}", "XXXXX")
        raise SmartHomeDeviceException(error_message, url_with_masked_device_id)

    def _parse_air_quality(self, data: dict) -> AirQuality:
        """
        辞書データからAirQualityオブジェクトを生成。

        Args:
            data (dict): デバイスのデータ

        Returns:
            AirQuality: 温度と湿度を含むオブジェクト
        """
        temperature = data["temperature"]
        humidity = data["humidity"]
        return AirQuality(temperature=temperature, humidity=humidity)

    def _parse_co2_sensor_data(self, data: dict) -> AirQuality:
        """
        辞書データからCO2SensorDataオブジェクトを生成。

        Args:
            data (dict): デバイスのデータ

        Returns:
            CO2SensorData: 温度、湿度、CO2濃度を含むオブジェクト
        """
        temperature = data["temperature"]
        humidity = data["humidity"]
        co2 = data["CO2"]
        return AirQuality(temperature=temperature, humidity=humidity, co2_level=co2)

    def _increase_circulator_volume(self) -> SmartHomeDeviceResponse:
        """
        スイッチボットに風量を増加させるコマンドを送信します。

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        return self._post_command(
            self._CIRCULATOR_DEVICE_ID,
            CirculatorFanSpeed.UP.label,
            "default",
            "customize",
        )

    def _decrease_circulator_volume(self) -> SmartHomeDeviceResponse:
        """
        スイッチボットに風量を減少させるコマンドを送信します。

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        return self._post_command(
            self._CIRCULATOR_DEVICE_ID,
            CirculatorFanSpeed.DOWN.label,
            "default",
            "customize",
        )

    def _generate_swt_header(self) -> Dict[str, str]:
        """
        SWTリクエスト用のヘッダーを生成します。

        Returns:
            headers (Dict[str, str]): 生成されたヘッダー。
        """
        # ACCESS_TOKENとSECRETを使用して署名を生成します
        t, sign, nonce = self._generate_sign(self._ACCESS_TOKEN, self._SECRET)

        # ヘッダーの辞書を作成します
        headers = {
            "Content-Type": "application/json; charset: utf8",
            "Authorization": self._ACCESS_TOKEN,
            "t": t,
            "sign": sign,
            "nonce": nonce,
        }
        return headers

    def _generate_sign(self, token: str, secret: str, nonce: str = "") -> tuple[str, str, str]:
        """
        トークン、シークレット、およびノンスから署名を生成します。

        Args:
            token (str): アクセストークン
            secret (str): シークレットキー
            nonce (str): ノンス (デフォルトは空文字列)

        Returns:
            tuple[str, str, str]: タイムスタンプ、署名、ノンスのタプル
        """
        t = int(round(time.time() * 1000))
        string_to_sign = "{}{}{}".format(token, t, nonce)
        string_to_sign = bytes(string_to_sign, "utf-8")
        sign = base64.b64encode(
            hmac.new(bytes(secret, "utf-8"), msg=string_to_sign, digestmod=hashlib.sha256).digest()
        )
        return (str(t), str(sign, "utf-8"), nonce)
