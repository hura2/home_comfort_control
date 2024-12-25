from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from shared.enums.power_mode import PowerMode


class AirconIntensityCalculator:
    """エアコン強度を計算するクラス"""

    @staticmethod
    def calculate_intensity(temperature: float, mode: str, fan_speed: str, power: str) -> int:
        if power == PowerMode.OFF.id:
            return 0

        # 温度スコア
        if mode in [AirconMode.COOLING.id, AirconMode.POWERFUL_COOLING.id]:
            if temperature <= 24:
                temp_score = 5
            elif temperature == 25:
                temp_score = 4
            elif temperature == 26:
                temp_score = 3
            elif temperature == 27:
                temp_score = 2
            else:
                temp_score = 1
        elif mode in [AirconMode.HEATING.id, AirconMode.POWERFUL_HEATING.id]:
            if temperature <= 24:
                temp_score = 5
            elif temperature == 25:
                temp_score = 4
            else:
                temp_score = 3
        else:
            temp_score = 0

        # 風量スコア
        if fan_speed == AirconFanSpeed.HIGH.id:
            fan_score = 3
        elif fan_speed == AirconFanSpeed.MEDIUM.id:
            fan_score = 2
        elif fan_speed == AirconFanSpeed.AUTO.id:
            fan_score = 2
        else:
            fan_score = 1

        # モードスコア
        if mode in [AirconMode.POWERFUL_COOLING.id, AirconMode.POWERFUL_HEATING.id]:
            mode_score = 4
        elif mode in [AirconMode.COOLING.id, AirconMode.HEATING.id]:
            mode_score = 3
        elif mode == AirconMode.DRY.id:
            mode_score = 2
        elif mode == AirconMode.FAN.id:
            mode_score = 0
        else:
            mode_score = 0

        return temp_score + fan_score + mode_score
