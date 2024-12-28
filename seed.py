# セッションを使用するためのコンテキスト管理
from db.db_session_manager import DBSessionManager
from models import Base
from models.aircon_change_interval_model import AirconChangeIntervalModel
from models.aircon_fan_speed_model import AirconFanSpeedModel
from models.aircon_mode_model import AirconModeModel
from models.sensor_type_model import SensorTypeModel
from shared.enums.aircon_fan_speed import AirconFanSpeed
from shared.enums.aircon_mode import AirconMode
from shared.enums.sensor_type import SensorType


def create_fan_speed_data_list():
    # Enum のメンバーを取得し、Attributes のリストを作成
    fan_speed_data = [
        AirconFanSpeedModel(id=fan_speed.id, name=fan_speed.name) for fan_speed in AirconFanSpeed
    ]

    return fan_speed_data


def create_aircon_mode_data_list():
    # Enum のメンバーを取得し、Attributes のリストを作成
    aircon_mode_data = [AirconModeModel(id=mode.id, name=mode.name) for mode in AirconMode]

    return aircon_mode_data


def create_sensor_type_data_list():
    # Enum のメンバーを取得し、Attributes のリストを作成
    sensor_type_data = [SensorTypeModel(id=type.id, name=type.name) for type in SensorType]

    return sensor_type_data


def create_aircon_change_interval_data_list():
    # Enum のメンバーを取得し、Attributes のリストを作成
    aircon_change_interval_data = []
    aircon_change_interval_data.append(
        AirconChangeIntervalModel(
            mode_id=AirconMode.COOLING.id,
            temperature_min=20,
            temperature_max=99,
            duration_minutes=60,
        )
    )
    aircon_change_interval_data.append(
        AirconChangeIntervalModel(
            mode_id=AirconMode.HEATING.id,
            temperature_min=-10,
            temperature_max=20,
            duration_minutes=30,
        )
    )
    aircon_change_interval_data.append(
        AirconChangeIntervalModel(
            mode_id=AirconMode.DRY.id,
            temperature_min=-99,
            temperature_max=99,
            duration_minutes=30,
        )
    )
    return aircon_change_interval_data


with DBSessionManager.auto_commit_session() as session:
    # まず、テーブルを削除
    Base.metadata.drop_all(bind=session.get_bind())

    # テーブルを再作成
    Base.metadata.create_all(bind=session.get_bind())

    sensor_types = create_sensor_type_data_list()
    aircon_modes = create_aircon_mode_data_list()
    fan_speeds = create_fan_speed_data_list()
    aircon_change_intervals = create_aircon_change_interval_data_list()

    session.add_all(sensor_types)
    session.add_all(aircon_modes)
    session.add_all(fan_speeds)
    session.add_all(aircon_change_intervals)
    print("すべてのデータが追加されました。")
