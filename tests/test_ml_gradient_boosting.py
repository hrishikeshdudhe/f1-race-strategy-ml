import pytest

from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
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


def test_invalid_number_of_estimators_is_rejected():
    with pytest.raises(
        ValueError,
        match="n_estimators must be greater than zero",
    ):
        StrategyGradientBoostingModel(
            n_estimators=0
        )


def test_invalid_learning_rate_is_rejected():
    with pytest.raises(
        ValueError,
        match="learning_rate must be greater than zero",
    ):
        StrategyGradientBoostingModel(
            learning_rate=0.0
        )


def test_invalid_max_depth_is_rejected():
    with pytest.raises(
        ValueError,
        match="max_depth must be greater than zero",
    ):
        StrategyGradientBoostingModel(
            max_depth=0
        )


def test_empty_training_data_is_rejected():
    model = StrategyGradientBoostingModel()

    with pytest.raises(
        ValueError,
        match="At least one training sample is required",
    ):
        model.fit([], [])


def test_feature_target_length_mismatch_is_rejected():
    model = StrategyGradientBoostingModel()

    features = create_features(5)
    targets = create_targets(4)

    with pytest.raises(
        ValueError,
        match="same length",
    ):
        model.fit(
            features,
            targets,
        )


def test_empty_feature_dictionary_is_rejected():
    model = StrategyGradientBoostingModel()

    with pytest.raises(
        ValueError,
        match="At least one feature is required",
    ):
        model.fit(
            [{}, {}],
            [1.0, 2.0],
        )


def test_prediction_before_training_is_rejected():
    model = StrategyGradientBoostingModel()

    with pytest.raises(
        RuntimeError,
        match="Model must be fitted before prediction",
    ):
        model.predict(
            create_features(2)
        )


def test_model_can_be_trained():
    model = StrategyGradientBoostingModel(
        n_estimators=20,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    model.fit(
        features,
        targets,
    )

    assert model.feature_names == [
        "feature_a",
        "feature_b",
    ]


def test_model_can_make_predictions():
    model = StrategyGradientBoostingModel(
        n_estimators=20,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    model.fit(
        features,
        targets,
    )

    predictions = model.predict(
        create_features(5)
    )

    assert len(predictions) == 5
    assert all(
        isinstance(
            prediction,
            float,
        )
        for prediction in predictions
    )


def test_feature_importances_are_available():
    model = StrategyGradientBoostingModel(
        n_estimators=20,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    model.fit(
        features,
        targets,
    )

    importances = model.feature_importances

    assert set(importances.keys()) == {
        "feature_a",
        "feature_b",
    }

    assert all(
        importance >= 0.0
        for importance in importances.values()
    )


def test_feature_importances_sum_to_one():
    model = StrategyGradientBoostingModel(
        n_estimators=20,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    model.fit(
        features,
        targets,
    )

    total_importance = sum(
        model.feature_importances.values()
    )

    assert total_importance == pytest.approx(
        1.0
    )