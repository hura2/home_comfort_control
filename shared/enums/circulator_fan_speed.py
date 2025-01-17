from shared.enums.attribute_enum import AttributesEnum
from shared.enums.attributes import Attributes


class CirculatorFanSpeed(AttributesEnum):
    """
    サーキュレーターのファン速度を表すEnumクラス。
    """

    UP = Attributes(1, "風力プラス")
    DOWN = Attributes(2, "風力マイナス")
