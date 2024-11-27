from enum import Enum


class AirconMode(Enum):
    """
    エアコンの動作モードを表すEnumクラス。
    """

    AUTO = ("1", "自動")  # 自動モード: エアコンが自動的に動作モードを選択します
    COOLING = ("2", "冷房")  # 冷房モード: エアコンが冷房モードで動作します
    DRY = ("3", "除湿")  # 除湿モード: エアコンが除湿モードで動作します
    FAN = ("4", "送風")  # 送風モード: エアコンが送風モードで動作します
    HEATING = ("5", "暖房")  # 暖房モード: エアコンが暖房モードで動作します
    POWERFUL_COOLING = ("101", "パワフル冷房")  # パワフル冷房: 強力な冷房モード
    POWERFUL_HEATING = ("102", "パワフル暖房")  # パワフル暖房: 強力な暖房モード

    def __init__(self, id, description):
        self.id = id
        self.description = description

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

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応する動作モードの説明を取得します。

        Args:
            id (str): 動作モードのID。

        Returns:
            str: 動作モードの説明。
        """
        return next((mode.description for mode in cls if mode.id == id), None)

    @classmethod
    def get_by_id(cls, id):
        """
        指定されたIDに対応する AirconMode の要素を取得します。

        Args:
            id (str): 動作モードのID。

        Returns:
            AirconMode: 対応する AirconMode の要素。見つからない場合は None。
        """
        for mode in cls:
            if mode.id == id:
                return mode
        return None


class AirconFanSpeed(Enum):
    """
    エアコンの風速を表すEnumクラス。
    """

    AUTO = ("1", "自動")  # 自動: エアコンが風速を自動で調整します
    LOW = ("2", "弱")  # 弱: 低い風速
    MEDIUM = ("3", "中")  # 中: 中程度の風速
    HIGH = ("4", "強")  # 強: 高い風速

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応する風速の説明を取得します。

        Args:
            id (str): 風速のID。

        Returns:
            str: 風速の説明。
        """
        return next((speed.description for speed in cls if speed.id == id), None)

    @classmethod
    def get_by_id(cls, id):
        """
        指定されたIDに対応する AirconFanSpeed の要素を取得します。

        Args:
            id (str): 動作モードのID。

        Returns:
            AirconFanSpeed: 対応する AirconFanSpeed の要素。見つからない場合は None。
        """
        for mode in cls:
            if mode.id == id:
                return mode
        return None


class AirconPower(Enum):
    """
    エアコンの電源状態を表すEnumクラス。
    """

    ON = ("on", "ON")  # ON: 電源がオンの状態
    OFF = ("off", "OFF")  # OFF: 電源がオフの状態

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応する電源状態の説明を取得します。

        Args:
            id (str): 電源状態のID。

        Returns:
            str: 電源状態の説明。
        """
        return next((state.description for state in cls if state.id == id), None)

    @classmethod
    def get_by_id(cls, id):
        """
        指定されたIDに対応する AirconPower の要素を取得します。

        Args:
            id (str): 動作モードのID。

        Returns:
            AirconPower: 対応する AirconPower の要素。見つからない場合は None。
        """
        for mode in cls:
            if mode.id == id:
                return mode
        return None


class CirculatorFanSpeed(Enum):
    """
    サーキュレーターの風速を表すEnumクラス。
    """

    UP = "風力プラス"  # 風力プラス: 風速を増加させる
    DOWN = "風力マイナス"  # 風力マイナス: 風速を減少させる


class CirculatorPower(Enum):
    """
    サーキュレーターの電源状態を表すEnumクラス。
    """

    ON = ("電源", "on")  # ON: 電源がオンの状態
    OFF = ("電源", "off")  # OFF: 電源がオフの状態

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応する電源状態の説明を取得します。

        Args:
            id (str): 電源状態のID。

        Returns:
            str: 電源状態の説明。
        """
        return next((state.description for state in cls if state.id == id), None)

    @classmethod
    def get_by_description(cls, description):
        """
        指定されたIDに対応する AirconPower の要素を取得します。

        Args:
            description (str): 動作モードの説明。

        Returns:
            AirconPower: 対応する AirconPower の要素。見つからない場合は None。
        """
        for mode in cls:
            if mode.description == description:
                return mode
        return None


class Location(Enum):
    """
    温度・湿度の計測場所を表すEnumクラス。
    """

    FLOOR = (1, "床")  # 床: 床近くの場所で温度と湿度を計測
    CEILING = (2, "天井")  # 天井: 天井近くの場所で温度と湿度を計測
    OUTDOOR = (3, "外")  # 外: 屋外の場所で温度と湿度を計測
    STUDY = (4, "書斎")  # 書斎: 書斎の場所で温度と湿度を計測
    BEDROOM = (5, "寝室")  # 寝室: 寝室の場所で温度と湿度とCO2を計測

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応する場所の説明を取得します。

        Args:
            id (int): 場所のID。

        Returns:
            str: 場所の説明。
        """
        return next((location.description for location in cls if location.id == id), None)


class SensorType(Enum):
    """センサーのタイプを定義するEnumクラス"""

    TEMPERATURE_HUMIDITY = ("temperature_humidity", "温湿度計")
    CO2 = ("co2", "CO2センサー")

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def get_by_description(cls, description):
        """
        指定されたIDに対応する SensorType の要素を取得します。

        Args:
            description (str): センサーの説明。

        Returns:
            SensorType: 対応する SensorType の要素。見つからない場合は None。
        """
        for mode in cls:
            if mode.description == description:
                return mode
        return None

    @classmethod
    def get_description(cls, id):
        """
        指定されたIDに対応するセンサーの説明を取得します。

        Args:
            id (str): センサーのID。

        Returns:
            str: センサーの説明。
        """
        return next((sensor.description for sensor in cls if sensor.id == id), None)


class SmartDeviceType(Enum):
    """
    スマートデバイスのタイプを定義するEnumクラス。
    """

    SWITCH_BOT = "SWITCHBOT"


from enum import Enum


class NotifierType(Enum):
    """
    通知方法を定義するEnumクラス。
    """
    LINE = "LINE"
    DISCORD = "DISCORD"

    @classmethod
    def from_value(cls, value: str):
        """
        指定された文字列に対応するEnumメンバーを取得します。

        Args:
            value (str): 通知方法を表す文字列。

        Returns:
            NotifierType: 該当するEnumメンバー。
        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"指定された通知方法 '{value}' は無効です。")


class NotificationCategory(Enum):
    """
    通知の優先度を定義するEnumクラス。
    """
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"

    @classmethod
    def from_value(cls, value: str):
        """
        指定された文字列に対応するEnumメンバーを取得します。

        Args:
            value (str): 通知優先度を表す文字列。

        Returns:
            NotificationCategory: 該当するEnumメンバー。
        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"指定された通知優先度 '{value}' は無効です。")
