from shared.enums.attribute_enum import AttributesEnum
from shared.enums.attributes import Attributes


class AirconFanSpeed(AttributesEnum):

    AUTO = Attributes(1, "自動")
    LOW = Attributes(2, "低")
    MEDIUM = Attributes(3, "中")
    HIGH = Attributes(4, "高")
