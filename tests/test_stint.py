import pytest

from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def test_stint_calculates_time():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    assert stint.total_time_seconds(90.0) == 268.65


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


def test_stint_with_fuel_is_slower_than_without_fuel():

    tire_without_fuel = Tire(TireCompound.MEDIUM)

    stint_without_fuel = Stint(
        tire=tire_without_fuel,
        number_of_laps=3,
    )

    time_without_fuel = (
        stint_without_fuel.total_time_seconds(90.0)
    )

    tire_with_fuel = Tire(TireCompound.MEDIUM)

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    stint_with_fuel = Stint(
        tire=tire_with_fuel,
        number_of_laps=3,
        fuel=fuel,
    )

    time_with_fuel = (
        stint_with_fuel.total_time_seconds(90.0)
    )

    assert time_with_fuel > time_without_fuel


def test_fuel_effect_decreases_as_fuel_burns():

    tire = Tire(TireCompound.MEDIUM)

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    stint = Stint(
        tire=tire,
        number_of_laps=3,
        fuel=fuel,
    )

    stint.total_time_seconds(90.0)

    assert fuel.remaining_fuel_kg() == 94.0


def test_fuel_time_penalty_is_applied_per_lap():

    tire = Tire(TireCompound.MEDIUM)

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    stint = Stint(
        tire=tire,
        number_of_laps=1,
        fuel=fuel,
        fuel_time_penalty_per_kg=0.03,
    )

    total_time = stint.total_time_seconds(90.0)

    expected = 90.0 - 0.5 + 3.0

    assert total_time == expected


def test_negative_fuel_penalty_is_rejected():

    tire = Tire(TireCompound.MEDIUM)

    with pytest.raises(ValueError):
        Stint(
            tire=tire,
            number_of_laps=3,
            fuel_time_penalty_per_kg=-0.01,
        )


def test_lap_time_seconds_calculates_single_lap():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    assert stint.lap_time_seconds(90.0) == 89.5


def test_lap_time_seconds_uses_current_fuel():

    tire = Tire(TireCompound.MEDIUM)

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    stint = Stint(
        tire=tire,
        number_of_laps=3,
        fuel=fuel,
    )

    first_lap = stint.lap_time_seconds(90.0)

    fuel.consume_one_lap()

    second_lap = stint.lap_time_seconds(90.0)

    assert first_lap == 92.5
    assert second_lap == 92.44
    assert second_lap < first_lap