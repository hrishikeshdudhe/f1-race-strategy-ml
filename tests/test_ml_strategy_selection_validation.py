import pytest

from f1_strategy.ml.strategy_selection_validation import (
    MLStrategySelectionValidator,
)


def create_validator():
    """Create a small validator for tests."""

    return MLStrategySelectionValidator(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_states=[1, 2, 3],
    )


def test_validation_returns_one_result_per_random_state():
    validator = create_validator()

    summary = validator.run()

    assert summary.number_of_runs == 3
    assert len(summary.results) == 3


def test_each_validation_run_has_training_and_candidate_strategies():
    validator = create_validator()

    summary = validator.run()

    for result in summary.results:
        assert result.training_strategies > 0
        assert result.candidate_strategies > 0
        assert (
            result.training_strategies
            + result.candidate_strategies
            == 81
        )


def test_selection_gap_is_non_negative():
    validator = create_validator()

    summary = validator.run()

    for result in summary.results:
        assert result.selection_gap >= 0.0


def test_summary_gap_statistics_are_consistent():
    validator = create_validator()

    summary = validator.run()

    gaps = [
        result.selection_gap
        for result in summary.results
    ]

    assert summary.minimum_selection_gap == min(gaps)
    assert summary.maximum_selection_gap == max(gaps)

    expected_average = (
        sum(gaps) / len(gaps)
    )

    assert summary.average_selection_gap == pytest.approx(
        expected_average
    )


def test_optimum_selection_count_is_consistent():
    validator = create_validator()

    summary = validator.run()

    expected_count = sum(
        result.selected_optimal
        for result in summary.results
    )

    assert (
        summary.exact_optimum_selections
        == expected_count
    )


def test_optimum_selection_rate_is_percentage():
    validator = create_validator()

    summary = validator.run()

    expected_rate = (
        summary.exact_optimum_selections
        / summary.number_of_runs
        * 100.0
    )

    assert summary.optimum_selection_rate == pytest.approx(
        expected_rate
    )


def test_empty_random_state_list_produces_empty_summary():
    validator = MLStrategySelectionValidator(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_states=[],
    )

    summary = validator.run()

    assert summary.number_of_runs == 0
    assert summary.exact_optimum_selections == 0
    assert summary.optimum_selection_rate == 0.0
    assert summary.average_selection_gap == 0.0
    assert summary.minimum_selection_gap == 0.0
    assert summary.maximum_selection_gap == 0.0


def test_invalid_number_of_laps_is_rejected():
    with pytest.raises(
        ValueError,
        match="Number of laps must be greater than one",
    ):
        MLStrategySelectionValidator(
            number_of_laps=1
        )


def test_invalid_base_lap_time_is_rejected():
    with pytest.raises(
        ValueError,
        match="Base lap time must be greater than zero",
    ):
        MLStrategySelectionValidator(
            base_lap_time=0.0
        )


def test_invalid_test_size_is_rejected():
    with pytest.raises(
        ValueError,
        match="test_size must be between zero and one",
    ):
        MLStrategySelectionValidator(
            test_size=1.0
        )