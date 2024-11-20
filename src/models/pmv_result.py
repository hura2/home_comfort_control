class PMVResult:
    """
    PMV（Predicted Mean Vote）計算結果を表すクラス。

    Attributes:
        pmv (float): PMV値（快適度指数）。
        ppd (float): PPD値（不快指数）。
        clo (float): 衣服の断熱性。
        air (float): 空気の速度。
        met (float): MET値（代謝当量）。
        wall (float): 壁表面温度。
        ceiling (float): 天井表面温度。
        floor (float): 床表面温度。
        mean_radiant_temperature (float): 平均放射温度。
        dry_bulb_temperature (float): 乾球温度。
        relative_air_speed (float): 相対風速。
        dynamic_clothing_insulation (float): 動的な衣服の断熱性。
    """

    def __init__(
        self,
        pmv: float,
        ppd: float,
        clo: float,
        air: float,
        met: float,
        wall: float,
        ceiling: float,
        floor: float,
        mean_radiant_temperature: float,
        dry_bulb_temperature: float,
        relative_air_speed: float,
        dynamic_clothing_insulation: float,
    ):
        # 属性の初期化とバリデーション
        self.pmv = pmv
        self.ppd = ppd
        self.clo = clo
        self.air = air
        self.met = met
        self.wall = wall
        self.ceiling = ceiling
        self.floor = floor
        self.mean_radiant_temperature = mean_radiant_temperature
        self.dry_bulb_temperature = dry_bulb_temperature
        self.relative_air_speed = relative_air_speed
        self.dynamic_clothing_insulation = dynamic_clothing_insulation

    @property
    def pmv(self) -> float:
        """PMV値（快適度指数）"""
        return self._pmv

    @pmv.setter
    def pmv(self, value: float) -> None:
        if not (-3 <= value <= 3):
            raise ValueError("PMV値は-3から3の範囲でなければなりません。")
        self._pmv = value

    @property
    def ppd(self) -> float:
        """PPD値（不快指数）"""
        return self._ppd

    @ppd.setter
    def ppd(self, value: float) -> None:
        if not (0 <= value <= 100):
            raise ValueError("PPD値は0から100の範囲でなければなりません。")
        self._ppd = value

    @property
    def clo(self) -> float:
        """衣服の断熱性"""
        return self._clo

    @clo.setter
    def clo(self, value: float) -> None:
        if value < 0:
            raise ValueError("衣服の断熱性は0以上でなければなりません。")
        self._clo = value

    @property
    def air(self) -> float:
        """空気の速度"""
        return self._air

    @air.setter
    def air(self, value: float) -> None:
        if value < 0:
            raise ValueError("空気の速度は0以上でなければなりません。")
        self._air = value

    @property
    def met(self) -> float:
        """MET値（代謝当量）"""
        return self._met

    @met.setter
    def met(self, value: float) -> None:
        if value < 0.6 or value > 3.0:
            raise ValueError("MET値は0.8〜3.0の範囲でなければなりません。")
        self._met = value

    @property
    def wall(self) -> float:
        """壁表面温度"""
        return self._wall

    @wall.setter
    def wall(self, value: float) -> None:
        self._wall = value

    @property
    def ceiling(self) -> float:
        """天井表面温度"""
        return self._ceiling

    @ceiling.setter
    def ceiling(self, value: float) -> None:
        self._ceiling = value

    @property
    def floor(self) -> float:
        """床表面温度"""
        return self._floor

    @floor.setter
    def floor(self, value: float) -> None:
        self._floor = value

    @property
    def mean_radiant_temperature(self) -> float:
        """平均放射温度"""
        return self._mean_radiant_temperature

    @mean_radiant_temperature.setter
    def mean_radiant_temperature(self, value: float) -> None:
        self._mean_radiant_temperature = value

    @property
    def dry_bulb_temperature(self) -> float:
        """乾球温度"""
        return self._dry_bulb_temperature

    @dry_bulb_temperature.setter
    def dry_bulb_temperature(self, value: float) -> None:
        self._dry_bulb_temperature = value

    @property
    def relative_air_speed(self) -> float:
        """相対風速"""
        return self._relative_air_speed

    @relative_air_speed.setter
    def relative_air_speed(self, value: float) -> None:
        self._relative_air_speed = value

    @property
    def dynamic_clothing_insulation(self) -> float:
        """動的な衣服の断熱性"""
        return self._dynamic_clothing_insulation

    @dynamic_clothing_insulation.setter
    def dynamic_clothing_insulation(self, value: float) -> None:
        self._dynamic_clothing_insulation = value
