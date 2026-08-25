from f1_strategy.simulation.race import Race
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.track import Track


def test_total_race_time_with_tire_degradation():
    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=3,
        average_speed_kmh=200.0,
    )

    tire = Tire(TireCompound.MEDIUM)

    race = Race(track, tire)

    total_time = race.total_race_time_seconds()

    assert total_time == 268.65

def test_tire_ages_during_race():
    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=3,
        average_speed_kmh=200.0,
    )

    tire = Tire(TireCompound.MEDIUM)

    race = Race(track, tire)

    race.total_race_time_seconds()

    assert tire.age == 3