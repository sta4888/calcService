from domain.value_objects.levels import level_by_volume
from domain.value_objects.level import Level


def test_level_zero():
    level = level_by_volume(0)
    assert isinstance(level, Level)

    assert level.percent == 0.0


def test_level_exact_threshold():
    assert level_by_volume(100).percent == 0.03
    assert level_by_volume(200).percent == 0.06
    assert level_by_volume(400).percent == 0.09


def test_level_between_thresholds():
    assert level_by_volume(350).percent == 0.06
    assert level_by_volume(799).percent == 0.09


def test_level_diff():
    high = Level(0.15)
    low = Level(0.06)

    assert high.diff(low) == 0.09
    assert low.diff(high) == 0.0
