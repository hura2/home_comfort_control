from shared.enums.attribute_enum import AttributesEnum
from shared.enums.attributes import Attributes


class SensorType(AttributesEnum):
    """センサーのタイプを定義するEnumクラス"""

    TEMPERATURE_HUMIDITY = Attributes(1, "温湿度計")
    CO2 = Attributes(2, "CO2センサー")
