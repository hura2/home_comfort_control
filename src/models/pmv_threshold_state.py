from models.aircon_state import AirconState


class PMVThresholdState:
    """PMVに基づくエアコンの設定を保持するクラス"""

    def __init__(self, threshold: float, aircon_state: AirconState):
        """
        初期化メソッド。

        Args:
            threshold (float): PMV閾値
            aircon_state (AirconState): エアコンの設定
        """
        self.threshold = threshold
        self.aircon_state = aircon_state

    @property
    def threshold(self):
        """PMV閾値のプロパティ"""
        return self._threshold

    @threshold.setter
    def threshold(self, value: float):
        """PMV閾値のセッター"""
        if not isinstance(value, (int, float)):
            raise ValueError("PMV閾値は数値である必要があります")
        self._threshold = value

    @property
    def aircon_state(self):
        """エアコン設定のプロパティ"""
        return self._aircon_state

    @aircon_state.setter
    def aircon_state(self, value: AirconState):
        """エアコン設定のセッター"""
        if not isinstance(value, AirconState):
            raise ValueError("エアコン設定はAirconState型である必要があります")
        self._aircon_state = value