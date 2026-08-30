import pytest
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race_condition import (
    RaceCondition,
)
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import (
    StrategyResult,
)
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import (
    Tire,
    TireCompound,
)


def create_sample_strategy():
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.MEDIUM),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )


def test_strategy_result_has_zero_condition_laps_without_schedule():
    strategy = create_sample_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=540.0,
    )

    assert result.race_condition_laps == 0
    assert result.green_laps == 0
    assert result.yellow_laps == 0
    assert result.vsc_laps == 0
    assert result.safety_car_laps == 0


def test_strategy_result_counts_race_conditions():
    strategy = create_sample_strategy()

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=2,
        end_lap=2,
        condition=RaceCondition.YELLOW,
    )

    schedule.set_condition(
        start_lap=3,
        end_lap=4,
        condition=RaceCondition.VSC,
    )

    schedule.set_condition(
        start_lap=5,
        end_lap=5,
        condition=RaceCondition.SAFETY_CAR,
    )

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=600.0,
        race_condition_schedule=schedule,
        base_lap_time=90.0,
    )

    assert result.green_laps == 2
    assert result.yellow_laps == 1
    assert result.vsc_laps == 2
    assert result.safety_car_laps == 1
    assert result.race_condition_laps == 4


def test_strategy_result_calculates_condition_delay():
    strategy = create_sample_strategy()

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=600.0,
        race_condition_schedule=schedule,
        base_lap_time=90.0,
    )

    expected_delay = 90.0 * 0.20

    assert (
        result.race_condition_delay_seconds
        == pytest.approx(expected_delay)
    )


def test_strategy_result_builds_condition_summary():
    strategy = create_sample_strategy()

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=2,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=600.0,
        race_condition_schedule=schedule,
        base_lap_time=90.0,
    )

    assert (
        result.race_condition_summary
        == "vsc:2"
    )


def test_strategy_result_normal_summary_without_incidents():
    strategy = create_sample_strategy()

    schedule = RaceConditionSchedule(6)

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=540.0,
        race_condition_schedule=schedule,
        base_lap_time=90.0,
    )

    assert (
        result.race_condition_summary
        == "normal"
    )