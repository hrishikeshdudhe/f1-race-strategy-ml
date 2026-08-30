from f1_strategy.ml.dataset import StrategyMLDataset
from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def make_strategy() -> RaceStrategy:
    """Create a simple two-stint strategy for testing."""

    first_stint = Stint(
        tire=Tire(TireCompound.SOFT),
        number_of_laps=20,
    )

    second_stint = Stint(
        tire=Tire(TireCompound.MEDIUM),
        number_of_laps=25,
    )

    pit_stop = PitStop(25.0)

    return RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[pit_stop],
    )


def make_result(
    total_time_seconds: float = 550.0,
) -> StrategyResult:
    """Create a strategy result for testing."""

    return StrategyResult(
        strategy=make_strategy(),
        total_time_seconds=total_time_seconds,
    )


def test_feature_extractor_returns_basic_strategy_features():
    strategy = make_strategy()

    extractor = StrategyFeatureExtractor()
    features = extractor.extract(strategy)

    assert features["number_of_stints"] == 2.0
    assert features["number_of_pit_stops"] == 1.0
    assert features["total_laps"] == 45.0
    assert features["pit_stop_time_seconds"] == 25.0


def test_feature_extractor_counts_tire_compounds():
    strategy = make_strategy()

    extractor = StrategyFeatureExtractor()
    features = extractor.extract(strategy)

    assert features["soft_stints"] == 1.0
    assert features["medium_stints"] == 1.0
    assert features["hard_stints"] == 0.0


def test_feature_extractor_returns_stint_lengths():
    strategy = make_strategy()

    extractor = StrategyFeatureExtractor()
    features = extractor.extract(strategy)

    assert features["stint_1_laps"] == 20.0
    assert features["stint_2_laps"] == 25.0


def test_ml_dataset_returns_correct_number_of_samples():
    results = [
        make_result(550.0),
        make_result(551.0),
        make_result(552.0),
    ]

    dataset = StrategyMLDataset(results)

    assert len(dataset) == 3


def test_ml_dataset_returns_features():
    results = [make_result()]

    dataset = StrategyMLDataset(results)

    features = dataset.features()

    assert len(features) == 1
    assert features[0]["number_of_stints"] == 2.0
    assert features[0]["total_laps"] == 45.0


def test_ml_dataset_returns_simulated_race_times_as_targets():
    results = [
        make_result(550.0),
        make_result(555.5),
    ]

    dataset = StrategyMLDataset(results)

    assert dataset.targets() == [550.0, 555.5]


def test_ml_dataset_returns_feature_names():
    results = [make_result()]

    dataset = StrategyMLDataset(results)

    names = dataset.feature_names()

    assert "number_of_stints" in names
    assert "number_of_pit_stops" in names
    assert "total_laps" in names
    assert "pit_stop_time_seconds" in names
    assert "soft_stints" in names
    assert "medium_stints" in names
    assert "hard_stints" in names
    assert "stint_1_laps" in names
    assert "stint_2_laps" in names


def test_empty_ml_dataset_has_no_features_or_targets():
    dataset = StrategyMLDataset([])

    assert len(dataset) == 0
    assert dataset.features() == []
    assert dataset.targets() == []
    assert dataset.feature_names() == []