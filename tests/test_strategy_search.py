import pytest

from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.run_strategy_search import (
    find_fastest_generated_strategy,
)


def test_generated_strategy_search_returns_strategy():

    strategy, race_time = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert strategy is not None
    assert race_time > 0.0


def test_generated_strategy_search_covers_entire_race():

    number_of_laps = 6

    strategy, _ = find_fastest_generated_strategy(
        number_of_laps=number_of_laps,
        base_lap_time=90.0,
    )

    assert strategy.total_laps() == number_of_laps


def test_generated_strategy_search_finds_two_stints():

    strategy, _ = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert len(strategy.stints) == 2
    assert len(strategy.pit_stops) == 1


def test_generated_strategy_search_uses_generated_strategies():

    strategy, race_time = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert strategy.total_laps() == 6
    assert len(strategy.stints) == 2
    assert len(strategy.pit_stops) == 1
    assert race_time > 0.0


def test_generated_strategy_search_accepts_race_condition_schedule():

    number_of_laps = 6

    schedule = RaceConditionSchedule(
        number_of_laps
    )

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    strategy, race_time = find_fastest_generated_strategy(
        number_of_laps=number_of_laps,
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    assert strategy is not None
    assert strategy.total_laps() == number_of_laps
    assert race_time > 0.0


def test_generated_strategy_search_with_safety_car_is_slower():

    number_of_laps = 6

    _, normal_time = (
        find_fastest_generated_strategy(
            number_of_laps=number_of_laps,
            base_lap_time=90.0,
        )
    )

    schedule = RaceConditionSchedule(
        number_of_laps
    )

    schedule.set_condition(
        start_lap=3,
        end_lap=4,
        condition=RaceCondition.SAFETY_CAR,
    )

    affected_strategy, affected_time = (
        find_fastest_generated_strategy(
            number_of_laps=number_of_laps,
            base_lap_time=90.0,
            race_condition_schedule=schedule,
        )
    )

    assert affected_strategy is not None
    assert affected_strategy.total_laps() == number_of_laps
    assert affected_time > normal_time