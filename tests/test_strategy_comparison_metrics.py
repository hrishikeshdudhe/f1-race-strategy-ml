import pytest

from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy(
    compound: TireCompound,
) -> RaceStrategy:
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(compound),
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


def test_fastest_strategy_has_zero_percentage_gap():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert results[0].time_gap_percentage == pytest.approx(
        0.0
    )


def test_slower_strategy_has_positive_percentage_gap():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert results[1].time_gap_percentage > 0.0


def test_gap_percentage_is_based_on_fastest_time():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    expected = (
        results[1].time_delta_seconds
        / results[0].total_time_seconds
    ) * 100.0

    assert results[1].time_gap_percentage == pytest.approx(
        expected
    )


def test_fastest_strategy_has_gap_to_next():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    expected = (
        results[1].total_time_seconds
        - results[0].total_time_seconds
    )

    assert results[0].time_gap_to_next_seconds == pytest.approx(
        expected
    )


def test_slowest_strategy_has_no_next_gap():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    assert results[-1].time_gap_to_next_seconds == pytest.approx(
        0.0
    )


def test_summary_contains_comparison_metrics():
    strategies = [
        create_strategy(TireCompound.SOFT),
        create_strategy(TireCompound.MEDIUM),
    ]

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies(
        strategies
    )

    summary = results[1].summary()

    assert "Time gap:" in summary
    assert "Gap to next:" in summary