import pytest

from f1_strategy.ml.baseline import MeanBaselineRegressor


def test_baseline_starts_unfitted():
    baseline = MeanBaselineRegressor()

    assert baseline.mean is None


def test_baseline_calculates_mean():
    baseline = MeanBaselineRegressor()

    baseline.fit(
        [100.0, 200.0, 300.0]
    )

    assert baseline.mean == pytest.approx(
        200.0
    )


def test_baseline_predicts_mean_for_requested_samples():
    baseline = MeanBaselineRegressor()

    baseline.fit(
        [100.0, 200.0, 300.0]
    )

    predictions = baseline.predict(3)

    assert predictions == pytest.approx(
        [200.0, 200.0, 200.0]
    )


def test_baseline_can_predict_zero_samples():
    baseline = MeanBaselineRegressor()

    baseline.fit(
        [100.0, 200.0, 300.0]
    )

    assert baseline.predict(0) == []


def test_baseline_rejects_empty_training_data():
    baseline = MeanBaselineRegressor()

    with pytest.raises(ValueError):
        baseline.fit([])


def test_baseline_requires_fitting_before_prediction():
    baseline = MeanBaselineRegressor()

    with pytest.raises(RuntimeError):
        baseline.predict(1)


def test_baseline_rejects_negative_prediction_count():
    baseline = MeanBaselineRegressor()

    baseline.fit([100.0])

    with pytest.raises(ValueError):
        baseline.predict(-1)