import pytest

from f1_strategy.ml.prediction import PredictionError
from f1_strategy.ml.prediction_summary import (
    PredictionErrorSummary,
)


def make_errors() -> list[PredictionError]:
    """Create deterministic prediction errors."""

    return [
        PredictionError(
            actual=100.0,
            predicted=102.0,
        ),
        PredictionError(
            actual=200.0,
            predicted=195.0,
        ),
        PredictionError(
            actual=300.0,
            predicted=309.0,
        ),
    ]


def test_empty_summary_returns_zero_values():
    summary = PredictionErrorSummary([])

    assert summary.mean_signed_error == 0.0
    assert summary.mean_absolute_error == 0.0
    assert summary.maximum_absolute_error == 0.0
    assert summary.minimum_absolute_error == 0.0


def test_calculates_mean_signed_error():
    summary = PredictionErrorSummary(
        make_errors()
    )

    assert summary.mean_signed_error == pytest.approx(
        2.0
    )


def test_calculates_mean_absolute_error():
    summary = PredictionErrorSummary(
        make_errors()
    )

    assert summary.mean_absolute_error == pytest.approx(
        16.0 / 3.0
    )


def test_calculates_maximum_absolute_error():
    summary = PredictionErrorSummary(
        make_errors()
    )

    assert summary.maximum_absolute_error == pytest.approx(
        9.0
    )


def test_calculates_minimum_absolute_error():
    summary = PredictionErrorSummary(
        make_errors()
    )

    assert summary.minimum_absolute_error == pytest.approx(
        2.0
    )


def test_returns_largest_errors_first():
    summary = PredictionErrorSummary(
        make_errors()
    )

    largest = summary.largest_errors(2)

    assert len(largest) == 2
    assert largest[0].absolute_error == pytest.approx(
        9.0
    )
    assert largest[1].absolute_error == pytest.approx(
        5.0
    )


def test_largest_errors_can_return_all_errors():
    summary = PredictionErrorSummary(
        make_errors()
    )

    largest = summary.largest_errors(10)

    assert len(largest) == 3


def test_largest_errors_zero_returns_empty_list():
    summary = PredictionErrorSummary(
        make_errors()
    )

    assert summary.largest_errors(0) == []


def test_negative_count_is_rejected():
    summary = PredictionErrorSummary(
        make_errors()
    )

    with pytest.raises(ValueError):
        summary.largest_errors(-1)