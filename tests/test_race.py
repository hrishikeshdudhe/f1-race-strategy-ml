from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race import Race
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.track import Track
import pytest

def test_total_race_time_with_multiple_stints():

    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=6,
        average_speed_kmh=200.0,
    )

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(
        tire=first_tire,
        number_of_laps=3,
    )

    second_stint = Stint(
        tire=second_tire,
        number_of_laps=3,
    )

    pit_stop = PitStop(20.0)

    strategy = RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
    )

    race = Race(
        track=track,
        strategy=strategy,
    )

    total_time = race.total_race_time_seconds()

    assert total_time == 558.74


def test_each_stint_ages_its_own_tire():

    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=6,
        average_speed_kmh=200.0,
    )

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(first_tire, 3)
    second_stint = Stint(second_tire, 3)

    pit_stop = PitStop(20.0)

    strategy = RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
    )

    race = Race(
        track=track,
        strategy=strategy,
    )

    race.total_race_time_seconds()

    assert first_tire.age == 3
    assert second_tire.age == 3

def test_strategy_must_cover_entire_race():

    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=6,
        average_speed_kmh=200.0,
    )

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(first_tire, 2)
    second_stint = Stint(second_tire, 3)

    pit_stop = PitStop(20.0)

    strategy = RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
    )

    with pytest.raises(ValueError):
        Race(
            track=track,
            strategy=strategy,
        )