import pytest

from f1_strategy.simulation.track import Track


def test_track_creation():
    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=50,
        average_speed_kmh=200.0,
    )

    assert track.name == "Demo Circuit"
    assert track.length_km == 5.0
    assert track.number_of_laps == 50
    assert track.average_speed_kmh == 200.0


def test_lap_time():
    track = Track(
        name="Demo Circuit",
        length_km=5.0,
        number_of_laps=50,
        average_speed_kmh=200.0,
    )

    assert track.lap_time_seconds() == 90.0


def test_invalid_track_length():
    with pytest.raises(ValueError):
        Track(
            name="Invalid Track",
            length_km=-5.0,
            number_of_laps=50,
            average_speed_kmh=200.0,
        )


def test_invalid_number_of_laps():
    with pytest.raises(ValueError):
        Track(
            name="Invalid Track",
            length_km=5.0,
            number_of_laps=0,
            average_speed_kmh=200.0,
        )


def test_invalid_average_speed():
    with pytest.raises(ValueError):
        Track(
            name="Invalid Track",
            length_km=5.0,
            number_of_laps=50,
            average_speed_kmh=-200.0,
        )