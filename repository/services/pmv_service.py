from sqlalchemy.orm import Session

from models.pmv_model import PmvModel
from repository.queries.pmv_queries import PmvQueries
from shared.dataclass.pmv_result import PMVResult


class PmvService:
    """
    PMV計算結果を管理するサービスクラス
    """

    def __init__(self, session: Session):
        """コンストラクタ"""
        # 各クエリクラスのインスタンスを初期化
        self.session = session
        self.pmv_queries = PmvQueries(session)

    def insert(self, measurement_id: int, pmv_result: PMVResult) -> PmvModel:
        """
        PMV計算結果をデータベースに挿入する

        Args:
            measurement_id (int): 測定値のID
            pmv_result (PMVResult): PMV計算結果

        Returns:
            PmvModel: 挿入されたPMV計算結果
        """
        return self.pmv_queries.insert(
            measurement_id=measurement_id,
            pmv=pmv_result.pmv,
            ppd=pmv_result.ppd,
            clo=pmv_result.clo,
            met=pmv_result.met,
            air_speed=pmv_result.air,
            relative_air_speed=pmv_result.relative_air_speed,
            dynamic_clo=pmv_result.dynamic_clothing_insulation,
            wall_surface_temperature=pmv_result.wall,
            mean_radiant_temperature=pmv_result.mean_radiant_temperature,
            dry_bulb_temperature=pmv_result.dry_bulb_temperature,
        )
