from shared.enums.attribute_enum import AttributesEnum
from shared.enums.attributes import Attributes


class AirconMode(AttributesEnum):

    AUTO = Attributes(1, "自動")
    COOLING = Attributes(2, "冷房")
    FAN = Attributes(3, "送風")
    DRY = Attributes(4, "ドライ")
    HEATING = Attributes(5, "暖房")
    POWERFUL_COOLING = Attributes(6, "パワフル冷房")
    POWERFUL_HEATING = Attributes(7, "パワフル暖房")

    def is_cooling(self) -> bool:
        """
        このモードが冷房かパワフル冷房かを判定します。

        Returns:
            bool: 冷房またはパワフル冷房の場合はTrue、それ以外はFalse。
        """
        return self in {AirconMode.COOLING, AirconMode.POWERFUL_COOLING}

    def is_heating(self) -> bool:
        """
        このモードが暖房かパワフル暖房かを判定します。

        Returns:
            bool: 暖房またはパワフル暖房の場合はTrue、それ以外はFalse。
        """
        return self in {AirconMode.HEATING, AirconMode.POWERFUL_HEATING}