import pytest

from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound


def test_strategy_calculates_total_time():

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
        stints=[
            first_stint,
            second_stint,
        ],
        pit_stops=[
            pit_stop,
        ],
    )

    assert strategy.total_time_seconds(90.0) == 558.74


def test_strategy_requires_one_more_stint_than_pit_stops():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    pit_stop = PitStop(20.0)

    with pytest.raises(ValueError):
        RaceStrategy(
            stints=[stint],
            pit_stops=[pit_stop],
        )


def test_strategy_with_one_stint_has_no_pit_stops():

    tire = Tire(TireCompound.MEDIUM)

    stint = Stint(
        tire=tire,
        number_of_laps=3,
    )

    strategy = RaceStrategy(
        stints=[stint],
        pit_stops=[],
    )

    assert strategy.total_time_seconds(90.0) == 268.65


def test_strategy_uses_shared_fuel_across_stints():

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

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    strategy = RaceStrategy(
        stints=[
            first_stint,
            second_stint,
        ],
        pit_stops=[
            pit_stop,
        ],
        fuel=fuel,
    )

    strategy.total_time_seconds(90.0)

    assert fuel.remaining_fuel_kg() == 88.0


def test_strategy_fuel_is_not_reset_at_pit_stop():

    first_tire = Tire(TireCompound.MEDIUM)
    second_tire = Tire(TireCompound.HARD)

    first_stint = Stint(
        tire=first_tire,
        number_of_laps=2,
    )

    second_stint = Stint(
        tire=second_tire,
        number_of_laps=2,
    )

    pit_stop = PitStop(20.0)

    fuel = Fuel(
        initial_mass_kg=100.0,
        consumption_per_lap_kg=2.0,
    )

    strategy = RaceStrategy(
        stints=[
            first_stint,
            second_stint,
        ],
        pit_stops=[
            pit_stop,
        ],
        fuel=fuel,
    )

    strategy.total_time_seconds(90.0)

    assert fuel.consumed_fuel_kg() == 8.0
    assert fuel.remaining_fuel_kg() == 92.0


def test_strategy_description_shows_compounds_and_laps():

    strategy = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.SOFT),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )

    assert strategy.description() == (
        "SOFT (3 laps) → HARD (3 laps)"
    )


def test_strategy_description_supports_multiple_stints():

    strategy = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.SOFT),
                number_of_laps=2,
            ),
            Stint(
                tire=Tire(TireCompound.MEDIUM),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=4,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
            PitStop(20.0),
        ],
    )

    assert strategy.description() == (
        "SOFT (2 laps) → MEDIUM (3 laps) → HARD (4 laps)"
    )


def test_strategy_description_does_not_modify_strategy():

    strategy = RaceStrategy(
        stints=[
            Stint(
                tire=Tire(TireCompound.MEDIUM),
                number_of_laps=3,
            ),
            Stint(
                tire=Tire(TireCompound.HARD),
                number_of_laps=3,
            ),
        ],
        pit_stops=[
            PitStop(20.0),
        ],
    )

    description = strategy.description()

    assert description == (
        "MEDIUM (3 laps) → HARD (3 laps)"
    )

    assert strategy.stints[0].tire.age == 0
    assert strategy.stints[1].tire.age == 0
    assert strategy.total_laps() == 6
