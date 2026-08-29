import pytest

from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def test_stint_calculates_time():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    total_time = stint.total_time_seconds(90.0)

    assert total_time == 268.65


def test_stint_ages_tire():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    stint.total_time_seconds(90.0)

    assert tire.age == 3


def test_stint_requires_positive_laps():

    tire = Tire(TireCompound.MEDIUM)

    with pytest.raises(ValueError):
        Stint(
            tire=tire,
            number_of_laps=0,
        )