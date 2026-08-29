import pytest

from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy(first_compound, second_compound):

    first_tire = Tire(first_compound)
    second_tire = Tire(second_compound)

    first_stint = Stint(first_tire, 3)
    second_stint = Stint(second_tire, 3)

    pit_stop = PitStop(20.0)

    return RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
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
    assert results[0][1] == 558.74
    assert results[1][1] == 557.33


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

    fastest_strategy, fastest_time = optimizer.find_fastest(
        [strategy_a, strategy_b]
    )

    assert fastest_strategy is strategy_b
    assert fastest_time == 557.33


def test_optimizer_requires_strategy():

    optimizer = StrategyOptimizer(90.0)

    with pytest.raises(ValueError):
        optimizer.find_fastest([])


def test_optimizer_evaluation_is_repeatable():

    strategy = create_strategy(
        TireCompound.MEDIUM,
        TireCompound.HARD,
    )

    optimizer = StrategyOptimizer(90.0)

    first_result = optimizer.evaluate([strategy])
    second_result = optimizer.evaluate([strategy])

    assert first_result[0][1] == second_result[0][1]