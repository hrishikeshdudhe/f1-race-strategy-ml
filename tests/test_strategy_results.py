import pytest

from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.strategy_results import StrategyResults


def create_result(time: float) -> StrategyResult:
    return StrategyResult(
        strategy=None,
        total_time_seconds=time,
    )


def test_results_contains_results():
    results = StrategyResults(
        [
            create_result(557.33),
            create_result(558.74),
        ]
    )

    assert len(results) == 2


def test_results_is_iterable():
    results = StrategyResults(
        [
            create_result(557.33),
            create_result(558.74),
        ]
    )

    times = [
        result.total_time_seconds
        for result in results
    ]

    assert times == [557.33, 558.74]


def test_results_supports_indexing():
    results = StrategyResults(
        [
            create_result(557.33),
            create_result(558.74),
        ]
    )

    assert results[0].total_time_seconds == 557.33


def test_results_best_returns_fastest():
    results = StrategyResults(
        [
            create_result(558.74),
            create_result(557.33),
            create_result(560.00),
        ]
    )

    assert results.best().total_time_seconds == 557.33


def test_results_top_n_returns_requested_results():
    results = StrategyResults(
        [
            create_result(557.33),
            create_result(558.74),
            create_result(560.00),
        ]
    )

    top_results = results.top_n(2)

    assert len(top_results) == 2
    assert top_results[0].total_time_seconds == 557.33
    assert top_results[1].total_time_seconds == 558.74


def test_results_count():
    results = StrategyResults(
        [
            create_result(557.33),
            create_result(558.74),
        ]
    )

    assert results.count() == 2


def test_results_fastest_time():
    results = StrategyResults(
        [
            create_result(558.74),
            create_result(557.33),
        ]
    )

    assert results.fastest_time_seconds() == pytest.approx(
        557.33
    )


def test_results_best_rejects_empty_collection():
    results = StrategyResults([])

    with pytest.raises(ValueError):
        results.best()


def test_results_rejects_negative_top_n():
    results = StrategyResults(
        [
            create_result(557.33),
        ]
    )

    with pytest.raises(ValueError):
        results.top_n(-1)


def test_optimizer_can_return_result_collection():
    from f1_strategy.simulation.optimizer import StrategyOptimizer
    from f1_strategy.simulation.pit_stop import PitStop
    from f1_strategy.simulation.strategy import RaceStrategy
    from f1_strategy.simulation.stint import Stint
    from f1_strategy.simulation.tire import Tire, TireCompound

    strategy_a = RaceStrategy(
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

    strategy_b = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.SOFT),
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

    optimizer = StrategyOptimizer(90.0)

    results = optimizer.rank_strategies_collection(
        [
            strategy_a,
            strategy_b,
        ]
    )

    assert isinstance(results, StrategyResults)
    assert len(results) == 2
    assert results.best().rank == 1