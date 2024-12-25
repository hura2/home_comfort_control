from sqlalchemy.orm import Session

from models.pmv_model import PmvModel


class PmvQueries:
    """PMV を管理するクエリクラス。"""

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): DB セッション
        """
        self.session = session

    def insert(
        self,
        measurement_id: int,
        pmv: float,
        ppd: float,
        clo: float,
        met: float,
        air_speed: float,
        relative_air_speed: float,
        dynamic_clo: float,
        wall_surface_temperature: float,
        mean_radiant_temperature: float,
        dry_bulb_temperature: float,
    ) -> PmvModel:
        """
        新しい PMV をデータベースに挿入する。
        
        Args:
            measurement_id (int): 測定値のID
            pmv (float): PMV値
            ppd (float): PPD値
            clo (float): 衣服の断熱性
            met (float): MET値
            air_speed (float): 空気の速度
            relative_air_speed (float): 相対風速
            dynamic_clo (float): 動的な衣服の断熱性
            wall_surface_temperature (float): 壁表面温度
            mean_radiant_temperature (float): 平均放射温度
            dry_bulb_temperature (float): 乾球温度
        Returns:
            PmvModel: 新しく挿入された PMV
        """
        new_pmv = PmvModel(
            measurement_id=measurement_id,
            pmv=pmv,
            ppd=ppd,
            clo=clo,
            met=met,
            air_speed=air_speed,
            relative_air_speed=relative_air_speed,
            dynamic_clo=dynamic_clo,
            wall_surface_temperature=wall_surface_temperature,
            mean_radiant_temperature=mean_radiant_temperature,
            dry_bulb_temperature=dry_bulb_temperature,
        )
        self.session.add(new_pmv)
        self.session.flush()
        return new_pmv
