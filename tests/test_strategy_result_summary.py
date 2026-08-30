from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def create_result(
    rank: int | None = 1,
) -> StrategyResult:
    strategy = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.SOFT),
                number_of_laps=2,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=4,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )

    return StrategyResult(
        strategy=strategy,
        total_time_seconds=558.0,
        rank=rank,
    )


def test_summary_contains_rank():
    result = create_result(rank=1)

    summary = result.summary()

    assert "Rank: 1" in summary


def test_summary_contains_race_time():
    result = create_result()

    summary = result.summary()

    assert "Total race time: 558.00 s" in summary


def test_summary_contains_average_lap_time():
    result = create_result()

    summary = result.summary()

    assert "Average lap time: 93.00 s" in summary


def test_summary_contains_stint_information():
    result = create_result()

    summary = result.summary()

    assert "Stints: 2" in summary
    assert "Stint laps: 2, 4" in summary


def test_summary_contains_tire_information():
    result = create_result()

    summary = result.summary()

    assert "Tires: SOFT -> HARD" in summary


def test_summary_contains_pit_stop_information():
    result = create_result()

    summary = result.summary()

    assert "Pit stops: 1" in summary
    assert "Pit stop time: 20.00 s" in summary


def test_summary_handles_missing_rank():
    result = create_result(rank=None)

    summary = result.summary()

    assert "Rank: N/A" in summary