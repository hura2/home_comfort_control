from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from models import AirconSettingModel
from repository.queries.aircon_fan_speed_queries import AirconFanSpeedQueries
from repository.queries.aircon_mode_queries import AirconModeQueries
from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from shared.enums.power_mode import PowerMode
from translations.translated_value_error import TranslatedValueError


class AirconSettingQueries:

    def __init__(self, session: Session):
        """
        コンストラクタ

        Args:
            session (Session): SQLAlchemyのセッションオブジェクト
        """
        self.session = session

    def insert(
        self,
        measurement_id: int,
        mode: AirconMode,
        fan_speed: AirconFanSpeed,
        power: PowerMode,
        temperature: float,
    ) -> AirconSettingModel:
        """
        新しいエアコン設定をデータベースに挿入する。

        Args:
            measurement_id (int): 測定値のID
            mode (AirconModeType): モード
            fan_speed (AirconFanSpeedType): ファン速度
            temperature (float): 設定された温度
        Returns:
            AirconSetting: 新しく挿入されたエアコン設定
        """
        # モードとファン速度の検証
        aircon_mode_model = AirconModeQueries(self.session).get_mode_by_name(mode.name)
        if aircon_mode_model is None:
            raise TranslatedValueError(mode=mode)

        aircon_fan_speed_model = AirconFanSpeedQueries(self.session).get_fan_speed_by_name(
            fan_speed.name
        )
        if aircon_fan_speed_model is None:
            raise TranslatedValueError(fan_speed=fan_speed)

        # 新しいエアコン設定を挿入
        aircon_setting = AirconSettingModel(
            measurement_id=measurement_id,
            temperature=temperature,
            mode_id=aircon_mode_model.id,
            fan_speed_id=aircon_fan_speed_model.id,
            power=power.name,
        )

        self.session.add(aircon_setting)
        self.session.flush()

        return aircon_setting

    def get_latest_aircon_settings(self) -> AirconSettingModel:
        """
        最新のエアコン設定情報を取得します。

        Returns:
            AirconSettingModel: 最新のエアコン設定情報
        """
        aircon_setting_model = (
            self.session.query(AirconSettingModel)
            .order_by(AirconSettingModel.created_at.desc())
            .first()
        )
        return aircon_setting_model

    def get_aircon_settings_by_date(
        self, start_datetime: str, end_datetime: str
    ) -> list[AirconSettingModel]:
        """
        指定した日付のエアコン設定を取得するメソッド。

        :param date: 日付（例: "2024-12-25"）
        :return: エアコン設定のリスト
        """

        return (
            self.session.query(AirconSettingModel)
            .filter(
                AirconSettingModel.created_at >= start_datetime,
                AirconSettingModel.created_at < end_datetime,
            )
            .all()
        )