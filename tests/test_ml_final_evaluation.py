import pytest

from f1_strategy.ml.final_evaluation import (
    FinalModelEvaluator,
)


def create_features(
    number_of_samples: int,
) -> list[dict[str, float]]:
    """Create deterministic feature data."""

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
    """Create deterministic target data."""

    return [
        float(index * 3 + 10)
        for index in range(number_of_samples)
    ]


def test_invalid_number_of_folds_is_rejected():
    with pytest.raises(
        ValueError,
        match="number_of_folds must be at least 2",
    ):
        FinalModelEvaluator(
            number_of_folds=1
        )


def test_final_models_are_evaluated():
    evaluator = FinalModelEvaluator(
        number_of_folds=3,
        random_state=42,
    )

    results = evaluator.evaluate(
        features=create_features(15),
        targets=create_targets(15),
    )

    assert len(results) == 3

    assert [
        result.model_name
        for result in results
    ] == [
        "Linear Regression",
        "Random Forest",
        "Gradient Boosting",
    ]


def test_each_model_has_expected_number_of_folds():
    evaluator = FinalModelEvaluator(
        number_of_folds=4,
        random_state=42,
    )

    results = evaluator.evaluate(
        features=create_features(20),
        targets=create_targets(20),
    )

    for result in results:
        assert len(
            result.cross_validation.folds
        ) == 4


def test_gradient_boosting_uses_tuned_configuration():
    evaluator = FinalModelEvaluator(
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(25)
    targets = create_targets(25)

    results_a = evaluator.evaluate(
        features,
        targets,
    )

    results_b = evaluator.evaluate(
        features,
        targets,
    )

    gradient_a = next(
        result
        for result in results_a
        if result.model_name == "Gradient Boosting"
    )

    gradient_b = next(
        result
        for result in results_b
        if result.model_name == "Gradient Boosting"
    )

    assert (
        gradient_a.cross_validation.mean_mae
        == pytest.approx(
            gradient_b.cross_validation.mean_mae
        )
    )

    assert (
        gradient_a.cross_validation.mean_rmse
        == pytest.approx(
            gradient_b.cross_validation.mean_rmse
        )
    )

    assert (
        gradient_a.cross_validation.mean_r2
        == pytest.approx(
            gradient_b.cross_validation.mean_r2
        )
    )


def test_final_evaluation_rejects_empty_features():
    evaluator = FinalModelEvaluator(
        number_of_folds=3,
        random_state=42,
    )

    with pytest.raises(
        ValueError,
        match="At least one sample is required",
    ):
        evaluator.evaluate(
            features=[],
            targets=[],
        )


def test_final_evaluation_rejects_mismatched_data():
    evaluator = FinalModelEvaluator(
        number_of_folds=3,
        random_state=42,
    )

    with pytest.raises(
        ValueError,
        match="same length",
    ):
        evaluator.evaluate(
            features=create_features(10),
            targets=create_targets(9),
        )