import pytest

from f1_strategy.simulation.constraints import StrategyConstraints
from f1_strategy.simulation.tire import Tire, TireCompound
from f1_strategy.simulation.stint import Stint


def test_constraints_have_default_values():

    constraints = StrategyConstraints()

    assert constraints.minimum_stint_laps == 1
    assert constraints.maximum_stint_laps is None
    assert constraints.minimum_pit_stops == 0
    assert constraints.maximum_pit_stops is None
    assert constraints.required_compounds is None


def test_constraints_accept_custom_values():

    constraints = StrategyConstraints(
        minimum_stint_laps=2,
        maximum_stint_laps=10,
        minimum_pit_stops=1,
        maximum_pit_stops=2,
        required_compounds={
            TireCompound.MEDIUM,
            TireCompound.HARD,
        },
    )

    assert constraints.minimum_stint_laps == 2
    assert constraints.maximum_stint_laps == 10
    assert constraints.minimum_pit_stops == 1
    assert constraints.maximum_pit_stops == 2
    assert constraints.required_compounds == {
        TireCompound.MEDIUM,
        TireCompound.HARD,
    }


def test_constraints_reject_zero_minimum_stint_laps():

    with pytest.raises(ValueError):

        StrategyConstraints(
            minimum_stint_laps=0,
        )


def test_constraints_reject_negative_minimum_stint_laps():

    with pytest.raises(ValueError):

        StrategyConstraints(
            minimum_stint_laps=-1,
        )


def test_constraints_reject_negative_minimum_pit_stops():

    with pytest.raises(ValueError):

        StrategyConstraints(
            minimum_pit_stops=-1,
        )


def test_constraints_reject_negative_maximum_pit_stops():

    with pytest.raises(ValueError):

        StrategyConstraints(
            maximum_pit_stops=-1,
        )


def test_constraints_reject_maximum_stint_laps_smaller_than_minimum():

    with pytest.raises(ValueError):

        StrategyConstraints(
            minimum_stint_laps=5,
            maximum_stint_laps=3,
        )


def test_constraints_reject_maximum_pit_stops_smaller_than_minimum():

    with pytest.raises(ValueError):

        StrategyConstraints(
            minimum_pit_stops=3,
            maximum_pit_stops=1,
        )


def test_constraints_accept_single_required_compound():

    constraints = StrategyConstraints(
        required_compounds={
            TireCompound.SOFT,
        }
    )

    assert constraints.required_compounds == {
        TireCompound.SOFT,
    }


def test_constraints_accept_multiple_required_compounds():

    constraints = StrategyConstraints(
        required_compounds={
            TireCompound.SOFT,
            TireCompound.MEDIUM,
            TireCompound.HARD,
        }
    )

    assert constraints.required_compounds == {
        TireCompound.SOFT,
        TireCompound.MEDIUM,
        TireCompound.HARD,
    }


def test_constraints_reject_empty_required_compounds():

    with pytest.raises(ValueError):

        StrategyConstraints(
            required_compounds=set(),
        )

def test_stint_length_constraint_accepts_valid_length():

    constraints = StrategyConstraints(
        minimum_stint_laps=2,
        maximum_stint_laps=5,
    )

    assert constraints.is_stint_length_valid(2)
    assert constraints.is_stint_length_valid(3)
    assert constraints.is_stint_length_valid(5)


def test_stint_length_constraint_rejects_invalid_length():

    constraints = StrategyConstraints(
        minimum_stint_laps=2,
        maximum_stint_laps=5,
    )

    assert not constraints.is_stint_length_valid(1)
    assert not constraints.is_stint_length_valid(6)


def test_pit_stop_constraint_accepts_valid_count():

    constraints = StrategyConstraints(
        minimum_pit_stops=1,
        maximum_pit_stops=2,
    )

    assert constraints.is_pit_stop_count_valid(1)
    assert constraints.is_pit_stop_count_valid(2)


def test_pit_stop_constraint_rejects_invalid_count():

    constraints = StrategyConstraints(
        minimum_pit_stops=1,
        maximum_pit_stops=2,
    )

    assert not constraints.is_pit_stop_count_valid(0)
    assert not constraints.is_pit_stop_count_valid(3)


def test_compound_constraint_accepts_required_compounds():

    constraints = StrategyConstraints(
        required_compounds={
            TireCompound.MEDIUM,
            TireCompound.HARD,
        }
    )

    stints = [
        Stint(
            tire=Tire(TireCompound.MEDIUM),
            number_of_laps=3,
        ),
        Stint(
            tire=Tire(TireCompound.HARD),
            number_of_laps=3,
        ),
    ]

    assert constraints.are_compounds_valid(stints)


def test_compound_constraint_rejects_missing_compound():

    constraints = StrategyConstraints(
        required_compounds={
            TireCompound.MEDIUM,
            TireCompound.HARD,
        }
    )

    stints = [
        Stint(
            tire=Tire(TireCompound.MEDIUM),
            number_of_laps=6,
        ),
    ]

    assert not constraints.are_compounds_valid(stints)