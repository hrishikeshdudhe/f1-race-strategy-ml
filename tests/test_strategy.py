import pytest

from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def test_strategy_calculates_total_time():

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(first_tire, 3)
    second_stint = Stint(second_tire, 3)

    pit_stop = PitStop(20.0)

    strategy = RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
    )

    total_time = strategy.total_time_seconds(90.0)

    assert total_time == 558.74


def test_strategy_requires_one_more_stint_than_pit_stops():

    tire = Tire(TireCompound.MEDIUM)
    stint = Stint(tire, 3)

    with pytest.raises(ValueError):
        RaceStrategy(
            stints=[stint],
            pit_stops=[PitStop(20.0)],
        )


def test_strategy_with_one_stint_has_no_pit_stops():

    tire = Tire(TireCompound.MEDIUM)
    stint = Stint(tire, 3)

    strategy = RaceStrategy(
        stints=[stint],
        pit_stops=[],
    )

    assert strategy.total_time_seconds(90.0) == 268.65