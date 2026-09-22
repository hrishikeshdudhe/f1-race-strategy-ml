from f1_strategy.application import (
    RaceStrategyApplication,
    RaceStrategyApplicationConfig,
)


def test_default_application_runs() -> None:
    application = RaceStrategyApplication()

    result = application.run()

    assert result.training_strategies == 352
    assert result.candidate_strategies == 89
    assert result.selection_gap >= 0.0


def test_application_config_is_used() -> None:
    config = RaceStrategyApplicationConfig(
        number_of_laps=20,
        base_lap_time=90.0,
        test_size=0.2,
        random_state=42,
    )

    application = RaceStrategyApplication(
        config=config
    )

    result = application.run()

    assert (
        result.training_strategies
        + result.candidate_strategies
        == 171
    )

    assert result.training_strategies == 136
    assert result.candidate_strategies == 35


def test_selection_time_matches_selected_strategy() -> None:
    application = RaceStrategyApplication()

    result = application.run()

    assert (
        result.selected_actual_time
        == result.selection.selected_strategy.total_time_seconds
    )


def test_fastest_time_matches_fastest_strategy() -> None:
    application = RaceStrategyApplication()

    result = application.run()

    assert (
        result.actual_fastest_time
        == result.actual_fastest_strategy.total_time_seconds
    )


def test_selection_gap_is_difference_between_times() -> None:
    application = RaceStrategyApplication()

    result = application.run()

    expected_gap = (
        result.selected_actual_time
        - result.actual_fastest_time
    )

    assert result.selection_gap == expected_gap


def test_invalid_configuration_is_rejected() -> None:
    try:
        RaceStrategyApplicationConfig(
            number_of_laps=1
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid configuration should raise ValueError"
        )