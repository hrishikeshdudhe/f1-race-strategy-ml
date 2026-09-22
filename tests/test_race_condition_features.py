from f1_strategy.ml.race_condition_features import (
    RaceConditionFeatureExtractor,
)
from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)


def create_result():
    generator = StrategyGenerator(
        number_of_laps=10,
    )

    strategies = (
        generator.generate_two_stint_strategies()
    )

    schedule = RaceConditionSchedule(
        number_of_laps=10,
        default_condition=RaceCondition.GREEN,
    )

    schedule.set_condition(
        start_lap=3,
        end_lap=4,
        condition=RaceCondition.YELLOW,
    )

    schedule.set_condition(
        start_lap=6,
        end_lap=6,
        condition=RaceCondition.VSC,
    )

    schedule.set_condition(
        start_lap=9,
        end_lap=9,
        condition=RaceCondition.SAFETY_CAR,
    )

    optimizer = StrategyOptimizer(
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    return optimizer.evaluate_detailed(
        strategies
    )[0]


def test_extractor_contains_strategy_features():
    result = create_result()

    extractor = RaceConditionFeatureExtractor()

    features = extractor.extract(result)

    assert "number_of_stints" in features
    assert "number_of_pit_stops" in features
    assert "soft_stints" in features


def test_extractor_contains_race_condition_features():
    result = create_result()

    extractor = RaceConditionFeatureExtractor()

    features = extractor.extract(result)

    assert features["green_laps"] == 6.0
    assert features["yellow_laps"] == 2.0
    assert features["vsc_laps"] == 1.0
    assert features["safety_car_laps"] == 1.0
    assert features["race_condition_laps"] == 4.0


def test_condition_laps_cover_entire_race():
    result = create_result()

    extractor = RaceConditionFeatureExtractor()

    features = extractor.extract(result)

    total_condition_laps = (
        features["green_laps"]
        + features["yellow_laps"]
        + features["vsc_laps"]
        + features["safety_car_laps"]
    )

    assert total_condition_laps == features["total_laps"]