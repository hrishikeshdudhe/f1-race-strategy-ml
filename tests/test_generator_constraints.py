from f1_strategy.simulation.constraints import StrategyConstraints
from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.tire import TireCompound


def test_generator_accepts_constraints():

    constraints = StrategyConstraints(
        minimum_stint_laps=2,
        maximum_stint_laps=4,
    )

    generator = StrategyGenerator(
        number_of_laps=6,
        constraints=constraints,
    )

    strategies = generator.generate_two_stint_strategies()

    assert strategies


def test_generator_respects_stint_length_constraints():

    constraints = StrategyConstraints(
        minimum_stint_laps=2,
        maximum_stint_laps=4,
    )

    generator = StrategyGenerator(
        number_of_laps=6,
        constraints=constraints,
    )

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        for stint in strategy.stints:
            assert 2 <= stint.number_of_laps <= 4


def test_generator_respects_required_compounds():

    constraints = StrategyConstraints(
        required_compounds={
            TireCompound.MEDIUM,
            TireCompound.HARD,
        }
    )

    generator = StrategyGenerator(
        number_of_laps=6,
        constraints=constraints,
    )

    strategies = generator.generate_two_stint_strategies()

    assert strategies

    for strategy in strategies:

        compounds = {
            stint.tire.compound
            for stint in strategy.stints
        }

        assert TireCompound.MEDIUM in compounds
        assert TireCompound.HARD in compounds


def test_generator_respects_pit_stop_constraints():

    constraints = StrategyConstraints(
        minimum_pit_stops=1,
        maximum_pit_stops=1,
    )

    generator = StrategyGenerator(
        number_of_laps=6,
        constraints=constraints,
    )

    strategies = generator.generate_two_stint_strategies()

    assert strategies

    for strategy in strategies:
        assert len(strategy.pit_stops) == 1


def test_generator_without_constraints_preserves_existing_behavior():

    generator = StrategyGenerator(
        number_of_laps=6,
    )

    strategies = generator.generate_two_stint_strategies()

    assert len(strategies) == 45