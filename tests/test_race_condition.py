from f1_strategy.simulation.race_condition import RaceCondition


def test_race_conditions_exist():

    assert RaceCondition.GREEN.label == "green"
    assert RaceCondition.YELLOW.label == "yellow"
    assert RaceCondition.VSC.label == "vsc"
    assert RaceCondition.SAFETY_CAR.label == "safety_car"


def test_green_condition_has_no_time_penalty():

    assert RaceCondition.GREEN.lap_time_multiplier == 1.00


def test_yellow_condition_is_slower_than_green():

    assert (
        RaceCondition.YELLOW.lap_time_multiplier
        > RaceCondition.GREEN.lap_time_multiplier
    )


def test_vsc_condition_is_slower_than_yellow():

    assert (
        RaceCondition.VSC.lap_time_multiplier
        > RaceCondition.YELLOW.lap_time_multiplier
    )


def test_safety_car_condition_is_slower_than_vsc():

    assert (
        RaceCondition.SAFETY_CAR.lap_time_multiplier
        > RaceCondition.VSC.lap_time_multiplier
    )


def test_all_race_conditions_have_positive_multipliers():

    for condition in RaceCondition:

        assert condition.lap_time_multiplier > 0


def test_race_conditions_are_different():

    multipliers = {
        condition.lap_time_multiplier
        for condition in RaceCondition
    }

    assert len(multipliers) == len(RaceCondition)