import pytest

from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy(
    first_compound: TireCompound,
    second_compound: TireCompound,
) -> RaceStrategy:
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(first_compound),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(second_compound),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )


def test_fastest_strategy_has_zero_time_delta():
    strategies = [
        create_strategy(
            TireCompound.MEDIUM,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.SOFT,
            TireCompound.HARD,
        ),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert results[0].time_delta_seconds == pytest.approx(
        0.0
    )


def test_slower_strategy_has_positive_time_delta():
    strategies = [
        create_strategy(
            TireCompound.MEDIUM,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.SOFT,
            TireCompound.HARD,
        ),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert results[1].time_delta_seconds > 0.0


def test_time_delta_matches_difference_from_fastest():
    strategies = [
        create_strategy(
            TireCompound.MEDIUM,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.SOFT,
            TireCompound.HARD,
        ),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    expected_delta = (
        results[1].total_time_seconds
        - results[0].total_time_seconds
    )

    assert results[1].time_delta_seconds == pytest.approx(
        expected_delta
    )


def test_time_delta_is_preserved_in_summary():
    strategies = [
        create_strategy(
            TireCompound.MEDIUM,
            TireCompound.HARD,
        ),
        create_strategy(
            TireCompound.SOFT,
            TireCompound.HARD,
        ),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    summary = results[1].summary()

    assert "Time difference:" in summary