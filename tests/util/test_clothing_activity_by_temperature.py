import datetime
import time
from unittest.mock import Mock, patch

import pytest

from settings.clothing_activity_by_temperature_settings import ClothingActivityByTemperatureSettings
from settings.general_settings import GeneralSettings
from util.clothing_activity_by_temperature import ClothingActivityByTemperature
from util.time import TimeUtil


@pytest.fixture
def mock_settings():
    """モックの設定インスタンスを返す。"""
    clothing_settings = ClothingActivityByTemperatureSettings()
    general_settings = GeneralSettings()
    return clothing_settings, general_settings


@pytest.fixture
def mock_time_util():
    """現在時刻を返すモックを作成し、datetimeオブジェクトを返す。"""
    with patch.object(
        TimeUtil, "get_current_time", return_value=datetime.datetime(2024, 11, 11, 16, 30)
    ):
        yield TimeUtil.get_current_time()


@pytest.mark.parametrize(
    "outdoor_temperature, max_temp, is_sleeping, expected_met, expected_icl",
    [
        (30.0, 35, False, 1.0, 0.7),  # 高温時、昼間
        (30.0, 35, True, 0.8, 0.8),  # 高温時、就寝
        (10.0, 15, False, 1.0, 1.0),  # 低温時、昼間
        (10.0, 15, True, 0.8, 2.0),  # 低温時、就寝
        (7.0, 15, False, 1.0, 1.0),  # 低温時、就寝
        (20.0, 25, False, 1.0, 0.75),  # 中温時、昼間
        (20.0, 25, True, 0.8, 1.6400000000000001),  # 中温時、就寝
    ],
)
def test_calculate_comfort_factors(
    outdoor_temperature,
    max_temp,
    is_sleeping,
    expected_met,
    expected_icl,
    mock_settings,
    mock_time_util,
):
    clothing_settings, general_settings = mock_settings

    # METとICLの計算
    comfort_factors = ClothingActivityByTemperature.calculate_comfort_factors(
        outdoor_temperature, max_temp, is_sleeping
    )

    # 結果の検証
    assert (
        comfort_factors.met == expected_met
    ), f"Expected MET: {expected_met}, but got: {comfort_factors.met}"
    assert (
        comfort_factors.icl == expected_icl
    ), f"Expected ICL: {expected_icl}, but got: {comfort_factors.icl}"


def test_calculate_high_temp_comfort_factors_daytime(mock_settings, mock_time_util):
    """高温時の昼間におけるComfortFactorsを正しく計算するかをテスト。"""
    clothing_settings, _ = mock_settings
    comfort_factors = ClothingActivityByTemperature.calculate_comfort_factors(
        32, 35, is_sleeping=False
    )
    assert comfort_factors.met == 1.0
    assert comfort_factors.icl == 0.7


def test_calculate_low_temp_comfort_factors_bedtime(mock_settings, mock_time_util):
    """低温時の就寝中におけるComfortFactorsを正しく計算するかをテスト。"""
    clothing_settings, _ = mock_settings
    comfort_factors = ClothingActivityByTemperature.calculate_comfort_factors(
        10, 12, is_sleeping=True
    )
    assert comfort_factors.met == 0.8
    assert comfort_factors.icl == 2.0


def test_calculate_high_temp_comfort_factors_bedtime(mock_settings, mock_time_util):
    """高温時の就寝中におけるComfortFactorsを正しく計算するかをテスト。"""
    clothing_settings, _ = mock_settings
    comfort_factors = ClothingActivityByTemperature.calculate_comfort_factors(
        32, 35, is_sleeping=True
    )
    assert comfort_factors.met == 0.8
    assert comfort_factors.icl == 0.8


@pytest.mark.parametrize(
    "current_time, lunch_time_settings, dinner_time_settings, pre_bedtime_settings, expected_met",
    [
        (
            datetime.time(14, 0),  # 現在時刻
            {
                "use": True,
                "start": datetime.time(13, 0),
                "end": datetime.time(15, 0),
                "met": 0.2,
            },  # 昼食時間帯設定
            {"use": False, "start": None, "end": None, "met": 0.0},  # 夕食時間帯設定
            {"use": False, "start": None, "end": None, "met": 0.0},  # 就寝前時間帯設定
            1.25,  # 期待されるMET
        ),
        (
            datetime.time(14, 30),  # 現在時刻
            {
                "use": True,
                "start": datetime.time(13, 0),
                "end": datetime.time(14, 0),
                "met": 0.2,
            },  # 昼食時間帯設定
            {
                "use": True,
                "start": datetime.time(14, 0),
                "end": datetime.time(16, 0),
                "met": 0.3,
            },  # 夕食時間帯設定
            {"use": False, "start": None, "end": None, "met": 0.0},  # 就寝前時間帯設定
            1.35,  # 期待されるMET
        ),
        (
            datetime.time(21, 30),  # 現在時刻
            {"use": False, "start": None, "end": None, "met": 0.0},  # 昼食時間帯設定
            {"use": False, "start": None, "end": None, "met": 0.0},  # 夕食時間帯設定
            {
                "use": True,
                "start": datetime.time(21, 0),
                "end": datetime.time(22, 0),
                "met": 0.4,
            },  # 就寝前時間帯設定
            1.45,  # 期待されるMET
        ),
        # 他のテストケースも同様に追加可能
    ],
)
def test_adjust_met_for_meal_times(
    mock_settings,
    current_time,
    lunch_time_settings,
    dinner_time_settings,
    pre_bedtime_settings,
    expected_met,
):
    """食事時間帯のMET調整をテスト。"""
    clothing_settings, _ = mock_settings

    # 高温時の設定をモックで再構築
    clothing_settings.high_temp_settings.time_settings = Mock()

    # 昼食時間設定
    clothing_settings.high_temp_settings.time_settings.lunch_time = Mock()
    clothing_settings.high_temp_settings.time_settings.lunch_time.use = lunch_time_settings["use"]
    clothing_settings.high_temp_settings.time_settings.lunch_time.start = lunch_time_settings[
        "start"
    ]
    clothing_settings.high_temp_settings.time_settings.lunch_time.end = lunch_time_settings["end"]
    clothing_settings.high_temp_settings.time_settings.lunch_time.met = lunch_time_settings["met"]

    # 夕食時間設定
    clothing_settings.high_temp_settings.time_settings.dinner_time = Mock()
    clothing_settings.high_temp_settings.time_settings.dinner_time.use = dinner_time_settings["use"]
    clothing_settings.high_temp_settings.time_settings.dinner_time.start = dinner_time_settings[
        "start"
    ]
    clothing_settings.high_temp_settings.time_settings.dinner_time.end = dinner_time_settings["end"]
    clothing_settings.high_temp_settings.time_settings.dinner_time.met = dinner_time_settings["met"]

    # 就寝前時間設定
    clothing_settings.high_temp_settings.time_settings.pre_bedtime = Mock()
    clothing_settings.high_temp_settings.time_settings.pre_bedtime.use = pre_bedtime_settings["use"]
    clothing_settings.high_temp_settings.time_settings.pre_bedtime.start = pre_bedtime_settings[
        "start"
    ]
    clothing_settings.high_temp_settings.time_settings.pre_bedtime.end = pre_bedtime_settings["end"]
    clothing_settings.high_temp_settings.time_settings.pre_bedtime.met = pre_bedtime_settings["met"]

    # 現在時刻をdatetimeで設定し、メソッドを実行
    now = datetime.datetime.combine(datetime.datetime.today(), current_time)
    met_adjusted = ClothingActivityByTemperature.adjust_met_for_meal_times(
        met=1.05, now=now, settings=clothing_settings
    )

    # 期待されるMETと一致するかを確認
    assert met_adjusted == expected_met, f"Expected MET: {expected_met}, but got: {met_adjusted}"
