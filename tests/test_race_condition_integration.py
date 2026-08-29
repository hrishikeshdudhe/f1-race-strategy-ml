import pytest

from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race import Race
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.track import Track


def create_strategy(number_of_laps: int) -> RaceStrategy:

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=number_of_laps,
    )

    return RaceStrategy(
        stints=[stint],
        pit_stops=[],
    )


def create_track(number_of_laps: int) -> Track:

    return Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=number_of_laps,
        average_speed_kmh=200.0,
    )


def test_race_uses_green_condition_by_default():

    track = create_track(3)
    strategy = create_strategy(3)

    race = Race(
        track=track,
        strategy=strategy,
    )

    expected_time = (
        3
        * track.lap_time_seconds()
        + (
            TireCompound.MEDIUM.lap_time_delta
            * 3
        )
    )

    assert race.race_condition_schedule.condition_for_lap(
        1
    ) == RaceCondition.GREEN

    assert race.race_condition_schedule.condition_for_lap(
        2
    ) == RaceCondition.GREEN

    assert race.race_condition_schedule.condition_for_lap(
        3
    ) == RaceCondition.GREEN


def test_race_condition_changes_total_race_time():

    track = create_track(3)

    normal_strategy = create_strategy(3)

    normal_race = Race(
        track=track,
        strategy=normal_strategy,
    )

    normal_time = normal_race.total_race_time_seconds()

    affected_strategy = create_strategy(3)

    schedule = RaceConditionSchedule(3)

    schedule.set_condition(
        start_lap=2,
        end_lap=2,
        condition=RaceCondition.VSC,
    )

    affected_race = Race(
        track=track,
        strategy=affected_strategy,
        race_condition_schedule=schedule,
    )

    affected_time = (
        affected_race.total_race_time_seconds()
    )

    assert affected_time > normal_time


def test_race_applies_condition_to_correct_lap():

    track = create_track(4)
    strategy = create_strategy(4)

    schedule = RaceConditionSchedule(4)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    race = Race(
        track=track,
        strategy=strategy,
        race_condition_schedule=schedule,
    )

    assert (
        race.race_condition_schedule.condition_for_lap(1)
        == RaceCondition.GREEN
    )

    assert (
        race.race_condition_schedule.condition_for_lap(2)
        == RaceCondition.GREEN
    )

    assert (
        race.race_condition_schedule.condition_for_lap(3)
        == RaceCondition.VSC
    )

    assert (
        race.race_condition_schedule.condition_for_lap(4)
        == RaceCondition.GREEN
    )


def test_race_schedule_must_match_track_lap_count():

    track = create_track(5)
    strategy = create_strategy(5)

    schedule = RaceConditionSchedule(4)

    with pytest.raises(ValueError):

        Race(
            track=track,
            strategy=strategy,
            race_condition_schedule=schedule,
        )


def test_race_condition_works_across_multiple_stints():

    track = create_track(6)

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(
        tire=first_tire,
        number_of_laps=3,
    )

    second_stint = Stint(
        tire=second_tire,
        number_of_laps=3,
    )

    strategy = RaceStrategy(
        stints=[
            first_stint,
            second_stint,
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=4,
        end_lap=5,
        condition=RaceCondition.SAFETY_CAR,
    )

    race = Race(
        track=track,
        strategy=strategy,
        race_condition_schedule=schedule,
    )

    assert (
        race.race_condition_schedule.condition_for_lap(3)
        == RaceCondition.GREEN
    )

    assert (
        race.race_condition_schedule.condition_for_lap(4)
        == RaceCondition.SAFETY_CAR
    )

    assert (
        race.race_condition_schedule.condition_for_lap(5)
        == RaceCondition.SAFETY_CAR
    )

    assert (
        race.race_condition_schedule.condition_for_lap(6)
        == RaceCondition.GREEN
    )