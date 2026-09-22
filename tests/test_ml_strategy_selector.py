import pytest

from f1_strategy.ml.strategy_selector import (
    MLStrategySelector,
)
from f1_strategy.simulation.strategy_result import StrategyResult


class FakeModel:
    """Simple deterministic model for selector testing."""

    def __init__(self, predictions):
        self._predictions = predictions

    def predict(self, features):
        return list(self._predictions)


class FakeFeatureExtractor:
    """Simple feature extractor for selector testing."""

    def extract(self, strategy):
        return {
            "test_feature": 1.0,
        }


def create_strategy() -> StrategyResult:
    """Create a lightweight strategy-result test object."""

    strategy = StrategyResult.__new__(StrategyResult)
    strategy.strategy = object()

    return strategy


def test_select_returns_strategy_with_lowest_prediction():
    strategies = [
        create_strategy(),
        create_strategy(),
        create_strategy(),
    ]

    model = FakeModel(
        predictions=[
            4525.0,
            4495.0,
            4515.0,
        ]
    )

    selector = MLStrategySelector(
        model=model,
        feature_extractor=FakeFeatureExtractor(),
    )

    result = selector.select(
        strategies=strategies,
    )

    assert result.selected_strategy is strategies[1]
    assert result.selected_prediction == 4495.0


def test_strategies_are_ranked_by_predicted_time():
    strategies = [
        create_strategy(),
        create_strategy(),
        create_strategy(),
    ]

    model = FakeModel(
        predictions=[
            4525.0,
            4495.0,
            4515.0,
        ]
    )

    selector = MLStrategySelector(
        model=model,
        feature_extractor=FakeFeatureExtractor(),
    )

    result = selector.select(
        strategies=strategies,
    )

    assert result.ranked_strategies[0].strategy is strategies[1]
    assert result.ranked_strategies[1].strategy is strategies[2]
    assert result.ranked_strategies[2].strategy is strategies[0]


def test_ranked_predictions_match_strategies():
    strategies = [
        create_strategy(),
        create_strategy(),
    ]

    model = FakeModel(
        predictions=[
            4505.0,
            4515.0,
        ]
    )

    selector = MLStrategySelector(
        model=model,
        feature_extractor=FakeFeatureExtractor(),
    )

    result = selector.select(
        strategies=strategies,
    )

    assert {
        prediction.strategy
        for prediction in result.ranked_strategies
    } == set(strategies)

    assert sorted(
        prediction.predicted_time
        for prediction in result.ranked_strategies
    ) == [4505.0, 4515.0]


def test_empty_strategy_list_is_rejected():
    model = FakeModel(
        predictions=[],
    )

    selector = MLStrategySelector(
        model=model,
        feature_extractor=FakeFeatureExtractor(),
    )

    with pytest.raises(
        ValueError,
        match="At least one strategy is required",
    ):
        selector.select([])


def test_model_prediction_count_must_match_strategy_count():
    strategies = [
        create_strategy(),
        create_strategy(),
    ]

    model = FakeModel(
        predictions=[4505.0],
    )

    selector = MLStrategySelector(
        model=model,
        feature_extractor=FakeFeatureExtractor(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "Model must return one prediction "
            "for each strategy"
        ),
    ):
        selector.select(strategies)