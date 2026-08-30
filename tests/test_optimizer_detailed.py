from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def create_strategy() -> RaceStrategy:
    first_stint = Stint(
        tire=Tire(TireCompound.SOFT),
        number_of_laps=3,
    )

    second_stint = Stint(
        tire=Tire(TireCompound.HARD),
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


def test_evaluate_detailed_returns_strategy_results():
    strategy = create_strategy()

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    results = optimizer.evaluate_detailed(
        [strategy]
    )

    assert len(results) == 1
    assert isinstance(
        results[0],
        StrategyResult,
    )


def test_evaluate_detailed_preserves_strategy():
    strategy = create_strategy()

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    results = optimizer.evaluate_detailed(
        [strategy]
    )

    assert results[0].strategy is strategy


def test_evaluate_detailed_calculates_total_time():
    strategy = create_strategy()

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    results = optimizer.evaluate_detailed(
        [strategy]
    )

    assert results[0].total_time_seconds > 0.0


def test_evaluate_detailed_contains_strategy_information():
    strategy = create_strategy()

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    result = optimizer.evaluate_detailed(
        [strategy]
    )[0]

    assert result.total_laps == 6
    assert result.number_of_pit_stops == 1
    assert result.pit_stop_time_seconds == 20.0
    assert result.tire_compounds == [
        "soft",
        "hard",
    ]


def test_evaluate_detailed_is_repeatable():
    strategy = create_strategy()

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
    )

    first_result = optimizer.evaluate_detailed(
        [strategy]
    )[0]

    second_result = optimizer.evaluate_detailed(
        [strategy]
    )[0]

    assert (
        first_result.total_time_seconds
        == second_result.total_time_seconds
    )