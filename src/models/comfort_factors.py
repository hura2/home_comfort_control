class ComfortFactors:
    """
    MET（代謝当量）およびICL（快適さ指標）を保持するクラス。

    Attributes:
        met (float): MET値。通常は1.0〜2.0程度（活動レベルに応じて異なる）
        icl (float): ICL値。通常は0.0〜1.5程度（衣服の断熱性に基づく）
    """

    def __init__(self, met: float, icl: float):
        """
        初期化メソッド。

        Args:
            met (float): MET値（0.8〜3.0の範囲で指定）
            icl (float): ICL値（0.0〜2.0の範囲で指定）
        """
        self.met = met
        self.icl = icl

    @property
    def met(self):
        """MET値のプロパティ"""
        return self._met

    @met.setter
    def met(self, value: float):
        """MET値のセッター"""
        if not (0.8 <= value <= 3.0):
            raise ValueError(f"MET値は0.8〜3.0の範囲である必要があります。指定された値: {value}")
        self._met = value

    @property
    def icl(self):
        """ICL値のプロパティ"""
        return self._icl

    @icl.setter
    def icl(self, value: float):
        """ICL値のセッター"""
        if not (0.0 <= value <= 2.0):
            raise ValueError(f"ICL値は0.0〜2.0の範囲である必要があります。指定された値: {value}")
        self._icl = value
