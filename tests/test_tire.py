from f1_strategy.simulation.tire import Tire, TireCompound


def test_tire_compounds_exist():
    assert TireCompound.SOFT.label == "soft"
    assert TireCompound.MEDIUM.label == "medium"
    assert TireCompound.HARD.label == "hard"


def test_new_tire_has_zero_age():
    tire = Tire(TireCompound.SOFT)

    assert tire.compound == TireCompound.SOFT
    assert tire.age == 0


def test_tire_can_start_with_existing_age():
    tire = Tire(TireCompound.MEDIUM, age=5)

    assert tire.compound == TireCompound.MEDIUM
    assert tire.age == 5


def test_tire_ages_by_one_lap():
    tire = Tire(TireCompound.HARD)

    tire.age_one_lap()

    assert tire.age == 1


def test_negative_tire_age_is_rejected():
    try:
        Tire(TireCompound.SOFT, age=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative tire age should raise ValueError")

def test_soft_compound_parameters():
    compound = TireCompound.SOFT

    assert compound.label == "soft"
    assert compound.pace_offset == -1.0
    assert compound.degradation_rate == 0.08


def test_compound_parameters_are_different():
    assert (
        TireCompound.SOFT.degradation_rate
        > TireCompound.HARD.degradation_rate
    )

    assert (
        TireCompound.SOFT.pace_offset
        < TireCompound.HARD.pace_offset
    )

def test_new_medium_tire_performance():
    tire = Tire(TireCompound.MEDIUM)

    assert tire.performance_delta() == -0.5


def test_tire_performance_degrades_with_age():
    tire = Tire(TireCompound.MEDIUM)

    tire.age = 5

    assert tire.performance_delta() == -0.25


def test_tire_performance_changes_after_lap():
    tire = Tire(TireCompound.SOFT)

    initial_delta = tire.performance_delta()

    tire.age_one_lap()

    new_delta = tire.performance_delta()

    assert new_delta > initial_delta