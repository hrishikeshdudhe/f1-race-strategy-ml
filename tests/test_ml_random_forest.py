import pytest

from f1_strategy.ml.random_forest import StrategyRandomForestModel


def sample_features() -> list[dict[str, float]]:
    return [
        {
            "number_of_stints": 2.0,
            "number_of_pit_stops": 1.0,
            "soft_stints": 1.0,
            "medium_stints": 1.0,
            "hard_stints": 0.0,
            "total_laps": 50.0,
        },
        {
            "number_of_stints": 2.0,
            "number_of_pit_stops": 1.0,
            "soft_stints": 0.0,
            "medium_stints": 1.0,
            "hard_stints": 1.0,
            "total_laps": 50.0,
        },
        {
            "number_of_stints": 3.0,
            "number_of_pit_stops": 2.0,
            "soft_stints": 1.0,
            "medium_stints": 1.0,
            "hard_stints": 1.0,
            "total_laps": 50.0,
        },
        {
            "number_of_stints": 2.0,
            "number_of_pit_stops": 1.0,
            "soft_stints": 0.0,
            "medium_stints": 2.0,
            "hard_stints": 0.0,
            "total_laps": 50.0,
        },
    ]


def sample_targets() -> list[float]:
    return [
        4500.0,
        4520.0,
        4550.0,
        4510.0,
    ]


def test_model_can_be_created():
    model = StrategyRandomForestModel()

    assert model.feature_names == []
    assert model.feature_importances == {}


def test_invalid_number_of_estimators_is_rejected():
    with pytest.raises(ValueError):
        StrategyRandomForestModel(n_estimators=0)


def test_negative_number_of_estimators_is_rejected():
    with pytest.raises(ValueError):
        StrategyRandomForestModel(n_estimators=-1)


def test_prediction_before_training_is_rejected():
    model = StrategyRandomForestModel()

    with pytest.raises(RuntimeError):
        model.predict(sample_features())


def test_empty_training_data_is_rejected():
    model = StrategyRandomForestModel()

    with pytest.raises(ValueError):
        model.fit([], [])


def test_mismatched_features_and_targets_are_rejected():
    model = StrategyRandomForestModel()

    features = sample_features()
    targets = sample_targets()[:-1]

    with pytest.raises(ValueError):
        model.fit(features, targets)


def test_empty_feature_dictionary_is_rejected():
    model = StrategyRandomForestModel()

    with pytest.raises(ValueError):
        model.fit([{}], [4500.0])


def test_model_can_be_trained():
    model = StrategyRandomForestModel(
        n_estimators=20,
        random_state=42,
    )

    model.fit(
        sample_features(),
        sample_targets(),
    )

    assert model.feature_names == list(
        sample_features()[0].keys()
    )


def test_model_can_make_predictions():
    model = StrategyRandomForestModel(
        n_estimators=20,
        random_state=42,
    )

    features = sample_features()

    model.fit(
        features,
        sample_targets(),
    )

    predictions = model.predict(features)

    assert len(predictions) == len(features)

    for prediction in predictions:
        assert isinstance(prediction, float)


def test_feature_importances_are_available_after_training():
    model = StrategyRandomForestModel(
        n_estimators=20,
        random_state=42,
    )

    model.fit(
        sample_features(),
        sample_targets(),
    )

    importances = model.feature_importances

    assert set(importances.keys()) == set(
        sample_features()[0].keys()
    )

    assert all(
        importance >= 0.0
        for importance in importances.values()
    )


def test_feature_importances_are_deterministic():
    features = sample_features()
    targets = sample_targets()

    model_a = StrategyRandomForestModel(
        n_estimators=20,
        random_state=42,
    )

    model_b = StrategyRandomForestModel(
        n_estimators=20,
        random_state=42,
    )

    model_a.fit(features, targets)
    model_b.fit(features, targets)

    assert model_a.feature_importances == (
        model_b.feature_importances
    )