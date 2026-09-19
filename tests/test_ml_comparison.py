import pytest

from f1_strategy.ml.comparison import (
    ModelComparator,
    ModelComparisonResult,
)
from f1_strategy.ml.model import StrategyRegressionModel
from f1_strategy.ml.random_forest import (
    StrategyRandomForestModel,
)


def sample_features() -> list[dict[str, float]]:
    return [
        {
            "stints": 2.0,
            "pit_stops": 1.0,
            "laps": 50.0,
        },
        {
            "stints": 2.0,
            "pit_stops": 1.0,
            "laps": 55.0,
        },
        {
            "stints": 3.0,
            "pit_stops": 2.0,
            "laps": 60.0,
        },
        {
            "stints": 3.0,
            "pit_stops": 2.0,
            "laps": 65.0,
        },
    ]


def sample_targets() -> list[float]:
    return [
        4500.0,
        4510.0,
        4525.0,
        4540.0,
    ]


def test_empty_model_collection_is_rejected():
    with pytest.raises(ValueError):
        ModelComparator({})


def test_empty_training_features_are_rejected():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    with pytest.raises(ValueError):
        comparator.evaluate(
            train_features=[],
            train_targets=[],
            test_features=sample_features(),
            test_targets=sample_targets(),
        )


def test_empty_test_features_are_rejected():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    with pytest.raises(ValueError):
        comparator.evaluate(
            train_features=sample_features(),
            train_targets=sample_targets(),
            test_features=[],
            test_targets=[],
        )


def test_training_feature_target_length_mismatch_is_rejected():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    with pytest.raises(ValueError):
        comparator.evaluate(
            train_features=sample_features(),
            train_targets=sample_targets()[:-1],
            test_features=sample_features(),
            test_targets=sample_targets(),
        )


def test_test_feature_target_length_mismatch_is_rejected():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    with pytest.raises(ValueError):
        comparator.evaluate(
            train_features=sample_features(),
            train_targets=sample_targets(),
            test_features=sample_features(),
            test_targets=sample_targets()[:-1],
        )


def test_single_model_can_be_evaluated():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    results = comparator.evaluate(
        train_features=sample_features(),
        train_targets=sample_targets(),
        test_features=sample_features(),
        test_targets=sample_targets(),
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(
        result,
        ModelComparisonResult,
    )

    assert result.model_name == "Linear Regression"

    assert result.metrics.mae >= 0.0
    assert result.metrics.rmse >= 0.0


def test_multiple_models_can_be_evaluated():
    comparator = ModelComparator(
        {
            "Linear Regression": StrategyRegressionModel(),
            "Random Forest": StrategyRandomForestModel(
                n_estimators=20,
                random_state=42,
            ),
        }
    )

    results = comparator.evaluate(
        train_features=sample_features(),
        train_targets=sample_targets(),
        test_features=sample_features(),
        test_targets=sample_targets(),
    )

    assert len(results) == 2

    assert results[0].model_name == "Linear Regression"
    assert results[1].model_name == "Random Forest"


def test_model_order_is_preserved():
    comparator = ModelComparator(
        {
            "Random Forest": StrategyRandomForestModel(
                n_estimators=20,
                random_state=42,
            ),
            "Linear Regression": StrategyRegressionModel(),
        }
    )

    results = comparator.evaluate(
        train_features=sample_features(),
        train_targets=sample_targets(),
        test_features=sample_features(),
        test_targets=sample_targets(),
    )

    assert [
        result.model_name
        for result in results
    ] == [
        "Random Forest",
        "Linear Regression",
    ]