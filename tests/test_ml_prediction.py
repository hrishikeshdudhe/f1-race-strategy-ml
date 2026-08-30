import pytest

from f1_strategy.ml.prediction import PredictionError


def test_prediction_error_calculates_signed_error():
    result = PredictionError(
        actual=100.0,
        predicted=105.0,
    )

    assert result.error == pytest.approx(5.0)


def test_prediction_error_calculates_negative_error():
    result = PredictionError(
        actual=105.0,
        predicted=100.0,
    )

    assert result.error == pytest.approx(-5.0)


def test_prediction_error_calculates_absolute_error():
    result = PredictionError(
        actual=105.0,
        predicted=100.0,
    )

    assert result.absolute_error == pytest.approx(
        5.0
    )


def test_prediction_error_handles_perfect_prediction():
    result = PredictionError(
        actual=100.0,
        predicted=100.0,
    )

    assert result.error == pytest.approx(0.0)
    assert result.absolute_error == pytest.approx(
        0.0
    )


def test_prediction_error_values_are_stored():
    result = PredictionError(
        actual=100.0,
        predicted=103.5,
    )

    assert result.actual == 100.0
    assert result.predicted == 103.5