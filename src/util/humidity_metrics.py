import math


class HumidityMetrics:

    @staticmethod
    def calculate_absolute_humidity(temperature: float, relative_humidity: float) -> float:
        """絶対湿度を計算するメソッド。

        Args:
            temperature (float): 温度（摂氏）
            relative_humidity (float): 相対湿度（％）

        Returns:
            float: 計算された絶対湿度（g/m³）
        """
        # 摂氏からケルビンに変換
        temperature_kelvin = temperature + 273.15

        # 飽和水蒸気圧の計算（hPa）
        saturated_vapor_pressure = 6.1078 * 10 ** ((7.5 * temperature) / (temperature + 237.3))

        # 絶対湿度の計算（g/m³）
        absolute_humidity = (
            217 * (relative_humidity / 100) * saturated_vapor_pressure
        ) / temperature_kelvin

        return absolute_humidity  # 絶対湿度を返す

    @staticmethod
    def calculate_dew_point(temperature_celsius: float, relative_humidity: float) -> float:
        """露点温度を計算するメソッド。

        Args:
            temperature_celsius (float): 温度（摂氏）
            relative_humidity (float): 相対湿度（％）

        Returns:
            float: 計算された露点温度（摂氏）
        """
        a = 17.27  # 定数
        b = 237.7  # 定数

        # αを計算
        alpha = ((a * temperature_celsius) / (b + temperature_celsius)) + math.log(
            relative_humidity / 100.0
        )

        # 露点温度の計算
        dew_point = math.ceil(((b * alpha) / (a - alpha)) * 10) / 10  # 小数点第一位まで切り上げ

        return dew_point  # 露点温度を返す
