import base64
import hashlib
import hmac
import json
import os
import time
from typing import Dict

import requests
from dotenv import load_dotenv

# 定数を管理するファイル
import common.constants as constants

# ロギング用のライブラリ
from models.air_quality import AirQuality
from models.aircon_state import AirconState
from models.sensor import Sensor
from util.logger import logger

# 環境変数の読み込み
load_dotenv(".env")


class SwitchBotApi:
    """
    SwitchBotApiクラスは、SwitchBotデバイスと通信するためのAPIを提供します。

    このクラスは、エアコンやサーキュレーターの操作、及び温度、湿度、CO2濃度データを取得するためのメソッドを含みます。
    クラスは環境変数からAPIアクセストークン、デバイスID、APIのベースURLを取得し、これらを使用してAPIリクエストを行います。
    """

    # 環境変数から読み込んだアクセストークンやデバイスIDを格納するクラス変数
    _ACCESS_TOKEN = os.environ["SWITCHBOT_ACCESS_TOKEN"]
    _SECRET = os.environ["SWITCHBOT_SECRET"]
    _CIRCULATOR_DEVICE_ID = os.environ["SWITCHBOT_CIRCULATOR_DEVICE_ID"]
    _AIR_CONDITIONER_DEVICE_ID = os.environ["SWITCHBOT_AIR_CONDITIONER_DEVICE_ID"]
    _AIR_CONDITIONER_SUPPORT_DEVICE_ID = os.environ["SWITCHBOT_AIR_CONDITIONER_SUPPORT_DEVICE_ID"]

    # APIのベースURL
    _API_BASE_URL = os.environ["SWITCHBOT_BASE_URL"]

    @staticmethod
    def increase_circulator_volume() -> requests.Response:
        """
        スイッチボットに風量を増加させるコマンドを送信します。

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        return SwitchBotApi._post_command(
            SwitchBotApi._CIRCULATOR_DEVICE_ID, constants.CirculatorFanSpeed.UP.value, "default", "customize"
        )

    @staticmethod
    def decrease_circulator_volume() -> requests.Response:
        """
        スイッチボットに風量を減少させるコマンドを送信します。

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        return SwitchBotApi._post_command(
            SwitchBotApi._CIRCULATOR_DEVICE_ID, constants.CirculatorFanSpeed.DOWN.value, "default", "customize"
        )

    @staticmethod
    def power_on_off() -> requests.Response:
        """
        スイッチボットに電源をオン/オフするコマンドを送信します。

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        return SwitchBotApi._post_command(
            SwitchBotApi._CIRCULATOR_DEVICE_ID, constants.CirculatorPower.ON.id, "default", "customize"
        )

    @staticmethod
    def aircon(settings: AirconState) -> requests.Response:
        """
        エアコンの設定を変更するコマンドを送信します。

        Args:
            settings (AirconState): エアコンの設定を含むオブジェクト

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        if settings.mode.id == constants.AirconMode.POWERFUL_COOLING.id:
            # パワフルモードは通常のエアコン設定では行えないため、別のデバイスIDで送信する
            return SwitchBotApi._post_command(
                SwitchBotApi._AIR_CONDITIONER_SUPPORT_DEVICE_ID,
                constants.AirconMode.POWERFUL_COOLING.description,
                "default",
                "customize",
            )

        if settings.mode.id == constants.AirconMode.POWERFUL_HEATING.id:
            # パワフルモードは通常のエアコン設定では行えないため、別のデバイスIDで送信する
            return SwitchBotApi._post_command(
                SwitchBotApi._AIR_CONDITIONER_SUPPORT_DEVICE_ID,
                constants.AirconMode.POWERFUL_HEATING.description,
                "default",
                "customize",
            )

        return SwitchBotApi._post_command(
            SwitchBotApi._AIR_CONDITIONER_DEVICE_ID,
            "setAll",
            f"{settings.temperature},{settings.mode.id},{settings.fan_speed.id},{settings.power.id}",
            "command",
        )

    @staticmethod
    def get_air_quality_by_sensor(sensor: Sensor) -> AirQuality:
        # 位置に応じたデバイスIDを取得
        device_id_key = f"SWITCHBOT_{sensor.id.upper()}_DEVICE_ID"
        device_id = os.getenv(device_id_key)
        if not device_id:
            raise ValueError(f"{device_id}のデバイスIDが環境変数に設定されていません。")

        if sensor.type == constants.SensorType.TEMPERATURE_HUMIDITY:
            # 温湿度データを取得
            return SwitchBotApi._get_temperature_and_humidity(device_id)
        elif sensor.type == constants.SensorType.CO2:
            # CO2データを取得
            return SwitchBotApi._get_co2_sensor_data(device_id)

    @staticmethod
    def _generate_swt_header() -> Dict[str, str]:
        """
        SWTリクエスト用のヘッダーを生成します。

        Returns:
            headers (Dict[str, str]): 生成されたヘッダー。
        """
        # ACCESS_TOKENとSECRETを使用して署名を生成します
        t, sign, nonce = SwitchBotApi._generate_sign(SwitchBotApi._ACCESS_TOKEN, SwitchBotApi._SECRET)

        # ヘッダーの辞書を作成します
        headers = {
            "Content-Type": "application/json; charset: utf8",
            "Authorization": SwitchBotApi._ACCESS_TOKEN,
            "t": t,
            "sign": sign,
            "nonce": nonce,
        }
        return headers

    @staticmethod
    def _generate_sign(token: str, secret: str, nonce: str = "") -> tuple[str, str, str]:
        """
        トークン、シークレット、およびノンスから署名を生成します。

        Args:
            token (str): アクセストークン
            secret (str): シークレットキー
            nonce (str, optional): ノンス (デフォルトは空文字列)

        Returns:
            tuple[str, str, str]: タイムスタンプ、署名、ノンスのタプル
        """
        t = int(round(time.time() * 1000))
        string_to_sign = "{}{}{}".format(token, t, nonce)
        string_to_sign = bytes(string_to_sign, "utf-8")
        secret = bytes(secret, "utf-8")
        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
        return (str(t), str(sign, "utf-8"), nonce)

    @staticmethod
    def _get_temperature_and_humidity(device_id: str) -> AirQuality:
        """
        指定したデバイスの温度と湿度を取得し、AirQualityオブジェクトを返します。

        Args:
            device_id (str): デバイスID

        Returns:
            AirQuality: 温度と湿度を格納したAirQualityオブジェクト
        """
        retry_count = 3  # リトライの試行回数
        retry_delay = 5  # リトライ間の遅延（秒）

        url = f"{SwitchBotApi._API_BASE_URL}/v1.1/devices/{device_id}/status"
        for _ in range(retry_count):
            try:
                with requests.Session() as session:
                    response = session.get(url, headers=SwitchBotApi._generate_swt_header())
                    response.raise_for_status()
                    data = response.json()
                    temperature = data["body"]["temperature"]
                    humidity = data["body"]["humidity"]
                    return AirQuality(temperature=temperature, humidity=humidity)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error occurred: {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        # リトライ後も成功しない場合はエラーを発生させる
        raise RuntimeError("Failed to retrieve temperature and humidity after multiple retries.")

    @staticmethod
    def _get_co2_sensor_data(device_id: str) -> AirQuality:
        """
        指定したCO2センサーの温度、湿度、CO2を取得し、CO2SensorDataオブジェクトを返します。

        Args:
            device_id (str): デバイスID

        Returns:
            CO2SensorData: 温度、湿度、CO2を格納したCO2SensorDataオブジェクト
        """
        retry_count = 3  # リトライの試行回数
        retry_delay = 5  # リトライ間の遅延（秒）

        url = f"{SwitchBotApi._API_BASE_URL}/v1.1/devices/{device_id}/status"
        for _ in range(retry_count):
            try:
                with requests.Session() as session:
                    response = session.get(url, headers=SwitchBotApi._generate_swt_header())
                    response.raise_for_status()
                    data = response.json()
                    temperature = data["body"]["temperature"]
                    humidity = data["body"]["humidity"]
                    co2 = data["body"]["CO2"]
                    # AirQualityのインスタンスを作成
                    return AirQuality(temperature=temperature, humidity=humidity, co2_level=co2)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error occurred: {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        # リトライ後も成功しない場合はエラーを発生させる
        raise RuntimeError("Failed to retrieve CO2 sensor data after multiple retries.")

    @staticmethod
    def _post_command(
        device_id: str, command: str, parameter: str = "default", command_type: str = "command"
    ) -> requests.Response:
        """
        指定したデバイスにコマンドを送信し、その結果を取得します。

        Args:
            device_id (str): デバイスID
            command (str): 送信するコマンド
            parameter (str, optional): コマンドのパラメータ（デフォルトは"default"）
            command_type (str, optional): コマンドの種類（デフォルトは"command"）

        Returns:
            requests.Response: コマンドの実行結果を表すResponseオブジェクト
        """
        url = f"{SwitchBotApi._API_BASE_URL}/v1.1/devices/{device_id}/commands"
        body = {"command": command, "parameter": parameter, "commandType": command_type}
        data = json.dumps(body)
        try:
            # コマンド送信前に一時停止（例: 0.5秒待つ）
            time.sleep(0.5)
            with requests.Session() as session:
                response = session.post(url, data=data, headers=SwitchBotApi._generate_swt_header())
            return response
        except requests.exceptions.RequestException as e:
            # エラーログを出力します
            logger.error(e)
