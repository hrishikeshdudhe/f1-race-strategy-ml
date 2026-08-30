from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.stint import Stint


def create_strategy(
    first_compound: TireCompound,
) -> RaceStrategy:
    return RaceStrategy(
        stints=[
            Stint(
                tire=Tire(first_compound),
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


def create_results():
    optimizer = StrategyOptimizer(90.0)

    return optimizer.rank_strategies_collection(
        [
            create_strategy(TireCompound.SOFT),
            create_strategy(TireCompound.MEDIUM),
            create_strategy(TireCompound.HARD),
        ]
    )


def test_report_contains_title():
    results = create_results()

    report = results.report()

    assert "F1 Strategy Report" in report


def test_report_contains_number_of_strategies():
    results = create_results()

    report = results.report()

    assert "Strategies evaluated: 3" in report


def test_report_contains_fastest_time():
    results = create_results()

    report = results.report()

    assert "Fastest race time:" in report


def test_report_contains_table_header():
    results = create_results()

    report = results.report()

    assert "Rank | Race Time | Gap | Gap % |" in report


def test_report_contains_ranked_strategies():
    results = create_results()

    report = results.report()

    assert "   1 |" in report
    assert "   2 |" in report
    assert "   3 |" in report


def test_report_can_limit_number_of_results():
    results = create_results()

    report = results.report(2)

    assert "   1 |" in report
    assert "   2 |" in report
    assert "   3 |" not in report


def test_report_without_results_is_readable():
    from f1_strategy.simulation.strategy_results import (
        StrategyResults,
    )

    results = StrategyResults([])

    assert results.report() == (
        "No strategy results."
    )