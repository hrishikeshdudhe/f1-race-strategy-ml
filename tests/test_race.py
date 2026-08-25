from f1_strategy.simulation.track import Track
from f1_strategy.simulation.race import Race


def test_total_race_time():
    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=50,
        average_speed_kmh=200.0,
    )

    race = Race(track)

    assert race.total_race_time_seconds() == 4500.0