import pytest

from f1_strategy.simulation.pit_stop import PitStop


def test_pit_stop_duration():

    pit_stop = PitStop(20.0)

    assert pit_stop.time_seconds() == 20.0


def test_pit_stop_requires_positive_duration():

    with pytest.raises(ValueError):
        PitStop(0.0)


def test_pit_stop_rejects_negative_duration():

    with pytest.raises(ValueError):
        PitStop(-5.0)