import pytest

from f1_strategy.ml.cross_validation import (
    CrossValidationResult,
    ModelCrossValidator,
)
from f1_strategy.ml.model import (
    StrategyRegressionModel,
)
from f1_strategy.ml.random_forest import (
    StrategyRandomForestModel,
)


def create_features(
    number_of_samples: int,
) -> list[dict[str, float]]:
    """Create a small deterministic feature dataset."""

    return [
        {
            "feature_a": float(index),
            "feature_b": float(index * 2),
        }
        for index in range(number_of_samples)
    ]


def create_targets(
    number_of_samples: int,
) -> list[float]:
    """Create deterministic regression targets."""

    return [
        float(index * 3 + 10)
        for index in range(number_of_samples)
    ]


def test_empty_model_collection_is_rejected():
    with pytest.raises(
        ValueError,
        match="At least one model is required",
    ):
        ModelCrossValidator({})


def test_invalid_number_of_folds_is_rejected():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    with pytest.raises(
        ValueError,
        match="number_of_folds must be at least 2",
    ):
        ModelCrossValidator(
            models,
            number_of_folds=1,
        )


def test_empty_features_are_rejected():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=2,
    )

    with pytest.raises(
        ValueError,
        match="At least one sample is required",
    ):
        validator.evaluate([], [])


def test_feature_target_length_mismatch_is_rejected():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=2,
    )

    features = create_features(4)
    targets = create_targets(3)

    with pytest.raises(
        ValueError,
        match="same length",
    ):
        validator.evaluate(
            features,
            targets,
        )


def test_too_few_samples_for_folds_are_rejected():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=5,
    )

    features = create_features(4)
    targets = create_targets(4)

    with pytest.raises(
        ValueError,
        match="number of folds",
    ):
        validator.evaluate(
            features,
            targets,
        )


def test_empty_feature_dictionary_is_rejected():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=2,
    )

    features = [
        {},
        {},
    ]

    targets = [
        1.0,
        2.0,
    ]

    with pytest.raises(
        ValueError,
        match="At least one feature is required",
    ):
        validator.evaluate(
            features,
            targets,
        )


def test_single_model_returns_expected_number_of_folds():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    results = validator.evaluate(
        features,
        targets,
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(
        result,
        CrossValidationResult,
    )

    assert result.model_name == "Linear Regression"
    assert len(result.folds) == 5


def test_fold_numbers_are_sequential():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    results = validator.evaluate(
        features,
        targets,
    )

    fold_numbers = [
        fold.fold_number
        for fold in results[0].folds
    ]

    assert fold_numbers == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_multiple_models_are_evaluated():
    models = {
        "Linear Regression": StrategyRegressionModel,
        "Random Forest": lambda: StrategyRandomForestModel(
            n_estimators=10,
            random_state=42,
        ),
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    results = validator.evaluate(
        features,
        targets,
    )

    assert len(results) == 2

    assert results[0].model_name == (
        "Linear Regression"
    )

    assert results[1].model_name == (
        "Random Forest"
    )


def test_model_order_is_preserved():
    models = {
        "Random Forest": lambda: StrategyRandomForestModel(
            n_estimators=10,
            random_state=42,
        ),
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=3,
        random_state=42,
    )

    features = create_features(15)
    targets = create_targets(15)

    results = validator.evaluate(
        features,
        targets,
    )

    assert [
        result.model_name
        for result in results
    ] == [
        "Random Forest",
        "Linear Regression",
    ]


def test_aggregate_metrics_are_calculated():
    models = {
        "Linear Regression": StrategyRegressionModel,
    }

    validator = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    results = validator.evaluate(
        features,
        targets,
    )

    result = results[0]

    assert result.mean_mae >= 0.0
    assert result.mean_rmse >= 0.0
    assert result.std_mae >= 0.0
    assert result.std_rmse >= 0.0
    assert result.std_r2 >= 0.0


def test_cross_validation_is_reproducible():
    models = {
        "Random Forest": lambda: StrategyRandomForestModel(
            n_estimators=10,
            random_state=42,
        ),
    }

    features = create_features(20)
    targets = create_targets(20)

    validator_a = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    validator_b = ModelCrossValidator(
        models,
        number_of_folds=5,
        random_state=42,
    )

    results_a = validator_a.evaluate(
        features,
        targets,
    )

    results_b = validator_b.evaluate(
        features,
        targets,
    )

    assert results_a[0].mean_mae == (
        results_b[0].mean_mae
    )

    assert results_a[0].mean_rmse == (
        results_b[0].mean_rmse
    )

    assert results_a[0].mean_r2 == (
        results_b[0].mean_r2
    )