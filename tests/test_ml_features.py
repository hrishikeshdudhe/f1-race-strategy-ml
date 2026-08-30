from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.tire import Tire, TireCompound


def make_strategy(
    stint_laps: list[int],
) -> RaceStrategy:
    """Create a strategy with the requested stint lengths."""

    compounds = [
        TireCompound.SOFT,
        TireCompound.MEDIUM,
        TireCompound.HARD,
    ]

    stints = []

    for index, laps in enumerate(stint_laps):
        compound = compounds[
            index % len(compounds)
        ]

        stints.append(
            Stint(
                tire=Tire(compound),
                number_of_laps=laps,
            )
        )

    pit_stops = [
        type(
            "TestPitStop",
            (),
            {
                "time_seconds": lambda self: 25.0
            },
        )()
        for _ in range(
            max(0, len(stints) - 1)
        )
    ]

    return RaceStrategy(
        stints=stints,
        pit_stops=pit_stops,
    )


def test_extracts_basic_strategy_features():
    strategy = make_strategy([20, 30])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["number_of_stints"] == 2.0
    assert features["number_of_pit_stops"] == 1.0
    assert features["total_laps"] == 50.0
    assert features["pit_stop_time_seconds"] == 25.0


def test_extracts_tire_compound_features():
    strategy = make_strategy([20, 30, 10])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["soft_stints"] == 1.0
    assert features["medium_stints"] == 1.0
    assert features["hard_stints"] == 1.0


def test_extracts_individual_stint_lengths():
    strategy = make_strategy([20, 30])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["stint_1_laps"] == 20.0
    assert features["stint_2_laps"] == 30.0


def test_calculates_average_stint_length():
    strategy = make_strategy([20, 30])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["average_stint_laps"] == 25.0


def test_calculates_shortest_stint_length():
    strategy = make_strategy([20, 30, 40])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["shortest_stint_laps"] == 20.0


def test_calculates_longest_stint_length():
    strategy = make_strategy([20, 30, 40])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["longest_stint_laps"] == 40.0


def test_calculates_stint_lap_range():
    strategy = make_strategy([20, 30, 40])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["stint_lap_range"] == 20.0


def test_equal_length_stints_have_zero_range():
    strategy = make_strategy([25, 25])

    features = StrategyFeatureExtractor().extract(
        strategy
    )

    assert features["average_stint_laps"] == 25.0
    assert features["shortest_stint_laps"] == 25.0
    assert features["longest_stint_laps"] == 25.0
    assert features["stint_lap_range"] == 0.0