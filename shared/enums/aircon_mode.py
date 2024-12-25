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

    @classmethod
    def is_cooling_mode(cls, mode: "AirconMode") -> bool:
        """
        指定されたモードが冷房関連のモードかどうかを判定します。

        :param mode: 判定するエアコンモード
        :return: 冷房関連のモードの場合はTrue、それ以外はFalse
        """
        return mode in {cls.COOLING, cls.POWERFUL_COOLING}

    @classmethod
    def is_heating_mode(cls, mode: "AirconMode") -> bool:
        """
        指定されたモードが暖房関連のモードかどうかを判定します。

        :param mode: 判定するエアコンモード
        :return: 暖房関連のモードの場合はTrue、それ以外はFalse
        """
        return mode in {cls.HEATING, cls.POWERFUL_HEATING}