import pytest

from f1_strategy.ml.metrics import RegressionMetrics


def test_mae_is_calculated_correctly():
    metrics = RegressionMetrics(
        actual=[10.0, 20.0, 30.0],
        predicted=[12.0, 18.0, 33.0],
    )

    assert metrics.mae == pytest.approx(
        7.0 / 3.0
    )


def test_rmse_is_calculated_correctly():
    metrics = RegressionMetrics(
        actual=[10.0, 20.0, 30.0],
        predicted=[12.0, 18.0, 33.0],
    )

    expected = (
        (4.0 + 4.0 + 9.0) / 3.0
    ) ** 0.5

    assert metrics.rmse == pytest.approx(
        expected
    )


def test_r2_is_one_for_perfect_predictions():
    metrics = RegressionMetrics(
        actual=[10.0, 20.0, 30.0],
        predicted=[10.0, 20.0, 30.0],
    )

    assert metrics.r2 == pytest.approx(1.0)


def test_all_metrics_are_zero_for_identical_zero_values():
    metrics = RegressionMetrics(
        actual=[0.0, 0.0, 0.0],
        predicted=[0.0, 0.0, 0.0],
    )

    assert metrics.mae == pytest.approx(0.0)
    assert metrics.rmse == pytest.approx(0.0)


def test_metrics_reject_empty_actual_values():
    with pytest.raises(ValueError):
        RegressionMetrics(
            actual=[],
            predicted=[],
        )


def test_metrics_reject_mismatched_lengths():
    with pytest.raises(ValueError):
        RegressionMetrics(
            actual=[10.0, 20.0],
            predicted=[10.0],
        )


def test_summary_contains_all_metrics():
    metrics = RegressionMetrics(
        actual=[10.0, 20.0, 30.0],
        predicted=[11.0, 21.0, 29.0],
    )

    summary = metrics.summary()

    assert "MAE:" in summary
    assert "RMSE:" in summary
    assert "R²:" in summary