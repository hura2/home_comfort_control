from shared.enums.attribute_enum import AttributesEnum
from shared.enums.attributes import Attributes


class PowerMode(AttributesEnum):
    ON = Attributes(1, "オン")
    OFF = Attributes(2, "オフ")
