from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.generator import StrategyGenerator


def test_generator_creates_expected_number_of_strategies():

    generator = StrategyGenerator(
        number_of_laps=6,
    )

    strategies = generator.generate_two_stint_strategies()

    assert len(strategies) == 45


def test_generated_strategies_cover_entire_race():

    generator = StrategyGenerator(
        number_of_laps=6,
    )

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        assert strategy.total_laps() == 6


def test_generated_strategies_have_two_stints():

    generator = StrategyGenerator(
        number_of_laps=6,
    )

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        assert len(strategy.stints) == 2
        assert len(strategy.pit_stops) == 1


def test_generator_can_create_fuelled_strategies():

    generator = StrategyGenerator(
        number_of_laps=6,
        initial_fuel_mass_kg=100.0,
        fuel_consumption_per_lap_kg=2.0,
    )

    strategies = generator.generate_two_stint_strategies()

    assert len(strategies) == 45

    for strategy in strategies:
        assert strategy.fuel is not None
        assert strategy.fuel.remaining_fuel_kg() == 100.0


def test_each_generated_strategy_has_independent_fuel():

    generator = StrategyGenerator(
        number_of_laps=6,
        initial_fuel_mass_kg=100.0,
        fuel_consumption_per_lap_kg=2.0,
    )

    strategies = generator.generate_two_stint_strategies()

    first_strategy = strategies[0]
    second_strategy = strategies[1]

    assert first_strategy.fuel is not second_strategy.fuel

    first_strategy.fuel.consume_one_lap()

    assert first_strategy.fuel.remaining_fuel_kg() == 98.0
    assert second_strategy.fuel.remaining_fuel_kg() == 100.0


def test_generator_accepts_different_fuel_consumption():

    generator = StrategyGenerator(
        number_of_laps=6,
        initial_fuel_mass_kg=100.0,
        fuel_consumption_per_lap_kg=1.5,
    )

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        assert strategy.fuel.consumption_per_lap_kg == 1.5


def test_generator_rejects_invalid_initial_fuel():

    try:
        StrategyGenerator(
            number_of_laps=6,
            initial_fuel_mass_kg=0.0,
        )
        assert False
    except ValueError:
        assert True


def test_generator_rejects_invalid_fuel_consumption():

    try:
        StrategyGenerator(
            number_of_laps=6,
            initial_fuel_mass_kg=100.0,
            fuel_consumption_per_lap_kg=0.0,
        )
        assert False
    except ValueError:
        assert True