from f1_strategy.ml.strategy_selection_experiment import (
    MLStrategySelectionExperiment,
    describe_strategy,
)


def test_experiment_returns_training_and_candidate_strategies():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    assert result.training_strategies > 0
    assert result.candidate_strategies > 0

    assert (
        result.training_strategies
        + result.candidate_strategies
        == 81
    )


def test_selected_strategy_is_one_of_the_candidates():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    candidate_strategies = {
        prediction.strategy
        for prediction in result.selection.ranked_strategies
    }

    assert (
        result.selection.selected_strategy
        in candidate_strategies
    )


def test_actual_fastest_strategy_is_one_of_the_candidates():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    candidate_strategies = {
        prediction.strategy
        for prediction in result.selection.ranked_strategies
    }

    assert (
        result.actual_fastest_strategy
        in candidate_strategies
    )


def test_selection_gap_is_non_negative():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    assert result.selection_gap >= 0.0


def test_selection_gap_matches_selected_and_optimal_times():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    expected_gap = (
        result.selected_actual_time
        - result.actual_fastest_time
    )

    assert result.selection_gap == expected_gap


def test_strategy_description_contains_tire_information():
    experiment = MLStrategySelectionExperiment(
        number_of_laps=10,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    result = experiment.run()

    description = describe_strategy(
        result.actual_fastest_strategy
    )

    assert "laps" in description
    assert "->" in description