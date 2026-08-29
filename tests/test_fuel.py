import pytest

from f1_strategy.simulation.fuel import Fuel


def test_fuel_starts_with_initial_mass():

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    assert fuel.remaining_fuel_kg() == 100.0


def test_fuel_consumes_one_lap():

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    fuel.consume_one_lap()

    assert fuel.remaining_fuel_kg() == 98.0


def test_fuel_consumption_is_accumulated():

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    fuel.consume_one_lap()
    fuel.consume_one_lap()
    fuel.consume_one_lap()

    assert fuel.consumed_fuel_kg() == 6.0
    assert fuel.remaining_fuel_kg() == 94.0


def test_fuel_does_not_become_negative():

    fuel = Fuel(
        initial_mass_kg=5.0,
        consumption_per_lap_kg=2.0,
    )

    for _ in range(5):
        fuel.consume_one_lap()

    assert fuel.remaining_fuel_kg() == 0.0


def test_initial_fuel_must_be_positive():

    with pytest.raises(ValueError):
        Fuel(
            initial_mass_kg=0.0,
            consumption_per_lap_kg=2.0,
        )


def test_fuel_consumption_must_be_positive():

    with pytest.raises(ValueError):
        Fuel(
            initial_mass_kg=100.0,
            consumption_per_lap_kg=0.0,
        )


def test_fuel_consumption_cannot_exceed_initial_mass():

    with pytest.raises(ValueError):
        Fuel(
            initial_mass_kg=10.0,
            consumption_per_lap_kg=11.0,
        )


def test_fuel_can_be_copied():

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    fuel.consume_one_lap()

    copied_fuel = fuel.copy()

    assert copied_fuel.remaining_fuel_kg() == 98.0
    assert copied_fuel is not fuel