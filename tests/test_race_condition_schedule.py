import pytest

from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)


def test_schedule_defaults_to_green():

    schedule = RaceConditionSchedule(10)

    assert (
        schedule.condition_for_lap(1)
        == RaceCondition.GREEN
    )

    assert (
        schedule.condition_for_lap(10)
        == RaceCondition.GREEN
    )


def test_schedule_can_use_custom_default_condition():

    schedule = RaceConditionSchedule(
        10,
        default_condition=RaceCondition.YELLOW,
    )

    assert (
        schedule.condition_for_lap(5)
        == RaceCondition.YELLOW
    )


def test_schedule_can_set_condition_for_lap_range():

    schedule = RaceConditionSchedule(10)

    schedule.set_condition(
        start_lap=4,
        end_lap=6,
        condition=RaceCondition.VSC,
    )

    assert (
        schedule.condition_for_lap(3)
        == RaceCondition.GREEN
    )

    assert (
        schedule.condition_for_lap(4)
        == RaceCondition.VSC
    )

    assert (
        schedule.condition_for_lap(5)
        == RaceCondition.VSC
    )

    assert (
        schedule.condition_for_lap(6)
        == RaceCondition.VSC
    )

    assert (
        schedule.condition_for_lap(7)
        == RaceCondition.GREEN
    )


def test_schedule_can_set_multiple_ranges():

    schedule = RaceConditionSchedule(20)

    schedule.set_condition(
        start_lap=5,
        end_lap=7,
        condition=RaceCondition.VSC,
    )

    schedule.set_condition(
        start_lap=12,
        end_lap=15,
        condition=RaceCondition.SAFETY_CAR,
    )

    assert (
        schedule.condition_for_lap(6)
        == RaceCondition.VSC
    )

    assert (
        schedule.condition_for_lap(10)
        == RaceCondition.GREEN
    )

    assert (
        schedule.condition_for_lap(13)
        == RaceCondition.SAFETY_CAR
    )


def test_later_condition_overrides_previous_condition():

    schedule = RaceConditionSchedule(10)

    schedule.set_condition(
        start_lap=3,
        end_lap=7,
        condition=RaceCondition.VSC,
    )

    schedule.set_condition(
        start_lap=5,
        end_lap=6,
        condition=RaceCondition.SAFETY_CAR,
    )

    assert (
        schedule.condition_for_lap(4)
        == RaceCondition.VSC
    )

    assert (
        schedule.condition_for_lap(5)
        == RaceCondition.SAFETY_CAR
    )

    assert (
        schedule.condition_for_lap(6)
        == RaceCondition.SAFETY_CAR
    )

    assert (
        schedule.condition_for_lap(7)
        == RaceCondition.VSC
    )


def test_schedule_rejects_invalid_number_of_laps():

    with pytest.raises(ValueError):

        RaceConditionSchedule(0)


def test_schedule_rejects_invalid_start_lap():

    schedule = RaceConditionSchedule(10)

    with pytest.raises(ValueError):

        schedule.set_condition(
            start_lap=0,
            end_lap=3,
            condition=RaceCondition.VSC,
        )


def test_schedule_rejects_end_lap_before_start_lap():

    schedule = RaceConditionSchedule(10)

    with pytest.raises(ValueError):

        schedule.set_condition(
            start_lap=5,
            end_lap=3,
            condition=RaceCondition.VSC,
        )


def test_schedule_rejects_end_lap_beyond_race():

    schedule = RaceConditionSchedule(10)

    with pytest.raises(ValueError):

        schedule.set_condition(
            start_lap=8,
            end_lap=11,
            condition=RaceCondition.VSC,
        )


def test_schedule_rejects_invalid_lap_lookup():

    schedule = RaceConditionSchedule(10)

    with pytest.raises(ValueError):

        schedule.condition_for_lap(0)

    with pytest.raises(ValueError):

        schedule.condition_for_lap(11)