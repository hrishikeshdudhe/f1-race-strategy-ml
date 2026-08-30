import pytest

from f1_strategy.ml.model import StrategyRegressionModel


def test_model_starts_unfitted():
    model = StrategyRegressionModel()

    assert model.feature_names == []
    assert model.coefficients == {}
    assert model.intercept is None


def test_model_rejects_empty_features():
    model = StrategyRegressionModel()

    with pytest.raises(ValueError):
        model.fit([], [])


def test_model_rejects_mismatched_features_and_targets():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
    ]

    targets = [100.0]

    with pytest.raises(ValueError):
        model.fit(
            features,
            targets,
        )


def test_model_rejects_empty_feature_dictionary():
    model = StrategyRegressionModel()

    with pytest.raises(ValueError):
        model.fit(
            [{}],
            [100.0],
        )


def test_model_predict_requires_fitting():
    model = StrategyRegressionModel()

    with pytest.raises(RuntimeError):
        model.predict(
            [{"laps": 10.0}]
        )


def test_model_trains_and_predicts():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
        {"laps": 30.0},
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    predictions = model.predict(
        [{"laps": 40.0}]
    )

    assert predictions == pytest.approx(
        [400.0]
    )


def test_model_exposes_feature_names():
    model = StrategyRegressionModel()

    features = [
        {
            "laps": 10.0,
            "pit_stops": 1.0,
        },
        {
            "laps": 20.0,
            "pit_stops": 2.0,
        },
        {
            "laps": 30.0,
            "pit_stops": 3.0,
        },
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    assert model.feature_names == [
        "laps",
        "pit_stops",
    ]


def test_model_exposes_coefficients():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
        {"laps": 30.0},
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    assert model.coefficients == {
        "laps": pytest.approx(10.0)
    }


def test_model_exposes_intercept():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
        {"laps": 30.0},
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    assert model.intercept == pytest.approx(
        0.0
    )


def test_model_coefficients_are_float_values():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
        {"laps": 30.0},
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    assert isinstance(
        model.coefficients["laps"],
        float,
    )


def test_model_intercept_is_float():
    model = StrategyRegressionModel()

    features = [
        {"laps": 10.0},
        {"laps": 20.0},
        {"laps": 30.0},
    ]

    targets = [
        100.0,
        200.0,
        300.0,
    ]

    model.fit(
        features,
        targets,
    )

    assert isinstance(
        model.intercept,
        float,
    )