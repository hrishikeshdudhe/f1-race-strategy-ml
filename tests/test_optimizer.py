import pytest

from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy(
    first_compound: TireCompound,
    second_compound: TireCompound,
) -> RaceStrategy:
    first_tire = Tire(first_compound)
    second_tire = Tire(second_compound)

    first_stint = Stint(
        tire=first_tire,
        number_of_laps=3,
    )

    second_stint = Stint(
        tire=second_tire,
        number_of_laps=3,
    )

    pit_stop = PitStop(20.0)

    return RaceStrategy(
        stints=[
            first_stint,
            second_stint,
        ],
        pit_stops=[
            pit_stop,
        ],
    )


def test_optimizer_evaluates_strategies():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.evaluate(
        [strategy_a, strategy_b]
    )

    assert len(results) == 2
    assert results[0][1] == pytest.approx(558.74)
    assert results[1][1] == pytest.approx(557.33)


def test_optimizer_finds_fastest_strategy():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    fastest_strategy, fastest_time = (
        optimizer.find_fastest(
            [strategy_a, strategy_b]
        )
    )

    assert fastest_strategy is strategy_b
    assert fastest_time == pytest.approx(557.33)


def test_optimizer_requires_strategy():

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.evaluate([])

    assert results == []


def test_optimizer_evaluation_is_repeatable():

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    first_results = optimizer.evaluate(
        [strategy]
    )

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    second_results = optimizer.evaluate(
        [strategy]
    )

    assert first_results[0][1] == pytest.approx(
        second_results[0][1]
    )


def test_optimizer_can_use_race_condition_schedule():

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    normal_optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    normal_time = normal_optimizer.find_fastest(
        [strategy]
    )[1]

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    affected_optimizer = StrategyOptimizer(
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    affected_time = affected_optimizer.find_fastest(
        [strategy]
    )[1]

    assert affected_time > normal_time


def test_optimizer_preserves_strategy_fuel():

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    strategy = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.MEDIUM),
                number_of_laps=6,
            )
        ],
        pit_stops=[],
        fuel=fuel,
    )

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.evaluate(
        [strategy]
    )

    assert results[0][1] == pytest.approx(
        strategy.total_time_seconds(90.0)
    )


def test_optimizer_applies_race_condition_to_correct_lap():

    strategy = RaceStrategy(
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

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=4,
        end_lap=4,
        condition=RaceCondition.SAFETY_CAR,
    )

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    _, race_time = optimizer.find_fastest(
        [strategy]
    )

    normal_optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    _, normal_time = normal_optimizer.find_fastest(
        [strategy]
    )

    expected_difference = (
        90.0
        * (
            RaceCondition.SAFETY_CAR.lap_time_multiplier
            - 1.0
        )
    )

    assert race_time == pytest.approx(
        normal_time + expected_difference
    )


def test_optimizer_does_not_modify_original_strategy():

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    initial_first_tire_age = (
        strategy.stints[0].tire.age
    )

    initial_second_tire_age = (
        strategy.stints[1].tire.age
    )

    optimizer = StrategyOptimizer(90.0)

    optimizer.evaluate([strategy])

    assert strategy.stints[0].tire.age == (
        initial_first_tire_age
    )

    assert strategy.stints[1].tire.age == (
        initial_second_tire_age
    )


def test_optimizer_ranks_strategies_fastest_first():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    ranked = optimizer.rank_strategies(
        [strategy_a, strategy_b]
    )

    assert len(ranked) == 2
    assert ranked[0][0] is strategy_b
    assert ranked[1][0] is strategy_a

    assert ranked[0][1] == pytest.approx(557.33)
    assert ranked[1][1] == pytest.approx(558.74)


def test_optimizer_ranking_matches_fastest_strategy():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    ranked = optimizer.rank_strategies(
        [strategy_a, strategy_b]
    )

    fastest_strategy, fastest_time = (
        optimizer.find_fastest(
            [strategy_a, strategy_b]
        )
    )

    assert ranked[0][0] is fastest_strategy
    assert ranked[0][1] == pytest.approx(
        fastest_time
    )


def test_optimizer_ranking_with_race_condition():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=4,
        condition=RaceCondition.SAFETY_CAR,
    )

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    ranked = optimizer.rank_strategies(
        [strategy_a, strategy_b]
    )

    assert len(ranked) == 2

    assert ranked[0][1] <= ranked[1][1]

    assert ranked[0][0] in (
        strategy_a,
        strategy_b,
    )

    assert ranked[1][0] in (
        strategy_a,
        strategy_b,
    )


def test_optimizer_ranking_does_not_modify_strategies():

    strategy_a = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    strategy_b = create_strategy(
        TireCompound.SOFT,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    optimizer.rank_strategies(
        [strategy_a, strategy_b]
    )

    assert strategy_a.stints[0].tire.age == 0
    assert strategy_a.stints[1].tire.age == 0

    assert strategy_b.stints[0].tire.age == 0
    assert strategy_b.stints[1].tire.age == 0
