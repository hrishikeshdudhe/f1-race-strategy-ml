import pytest

from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.tire import TireCompound


def test_generator_creates_all_two_stint_compound_and_length_combinations():

    generator = StrategyGenerator(6)

    strategies = generator.generate_two_stint_strategies()

    assert len(strategies) == 45


def test_generated_strategies_cover_entire_race():

    generator = StrategyGenerator(6)

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        assert strategy.total_laps() == 6


def test_generated_strategies_have_two_stints():

    generator = StrategyGenerator(6)

    strategies = generator.generate_two_stint_strategies()

    for strategy in strategies:
        assert len(strategy.stints) == 2


def test_generated_strategies_use_all_tire_compounds():

    generator = StrategyGenerator(6)

    strategies = generator.generate_two_stint_strategies()

    compounds = {
        (
            strategy.stints[0].tire.compound,
            strategy.stints[1].tire.compound,
        )
        for strategy in strategies
    }

    expected = {
        (first, second)
        for first in TireCompound
        for second in TireCompound
    }

    assert compounds == expected


def test_generated_strategies_use_all_possible_stint_lengths():

    generator = StrategyGenerator(6)

    strategies = generator.generate_two_stint_strategies()

    splits = {
        (
            strategy.stints[0].number_of_laps,
            strategy.stints[1].number_of_laps,
        )
        for strategy in strategies
    }

    expected = {
        (1, 5),
        (2, 4),
        (3, 3),
        (4, 2),
        (5, 1),
    }

    assert splits == expected


def test_generator_requires_more_than_one_lap():

    with pytest.raises(ValueError):
        StrategyGenerator(1)


def test_generator_requires_positive_laps():

    with pytest.raises(ValueError):
        StrategyGenerator(0)