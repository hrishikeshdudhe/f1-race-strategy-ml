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


def test_strategy_result_stores_strategy():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.strategy is strategy


def test_strategy_result_stores_total_time():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.total_time_seconds == 557.33


def test_strategy_result_calculates_pit_stop_time():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.pit_stop_time_seconds == 20.0


def test_strategy_result_counts_pit_stops():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.number_of_pit_stops == 1


def test_strategy_result_returns_total_laps():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.total_laps == 6


def test_strategy_result_returns_tire_compounds():
    strategy = create_strategy()

    result = StrategyResult(
        strategy=strategy,
        total_time_seconds=557.33,
    )

    assert result.tire_compounds == [
        "soft",
        "hard",
    ]