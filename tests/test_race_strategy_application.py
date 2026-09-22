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


def test_pit_stop_time_configuration_changes_race_time() -> None:
    default_config = RaceStrategyApplicationConfig(
        pit_stop_time_seconds=20.0,
    )

    increased_pit_stop_config = RaceStrategyApplicationConfig(
        pit_stop_time_seconds=30.0,
    )

    default_result = RaceStrategyApplication(
        config=default_config
    ).run()

    increased_pit_stop_result = RaceStrategyApplication(
        config=increased_pit_stop_config
    ).run()

    assert (
        increased_pit_stop_result.selected_actual_time
        - default_result.selected_actual_time
        == 10.0
    )

    assert (
        increased_pit_stop_result.actual_fastest_time
        - default_result.actual_fastest_time
        == 10.0
    )


def test_custom_pit_stop_time_is_used() -> None:
    config = RaceStrategyApplicationConfig(
        pit_stop_time_seconds=25.0,
    )

    application = RaceStrategyApplication(
        config=config
    )

    result = application.run()

    default_config = RaceStrategyApplicationConfig(
        pit_stop_time_seconds=20.0,
    )

    default_result = RaceStrategyApplication(
        config=default_config
    ).run()

    assert (
        result.selected_actual_time
        - default_result.selected_actual_time
        == 5.0
    )


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
            "Invalid number_of_laps should raise ValueError"
        )

    try:
        RaceStrategyApplicationConfig(
            pit_stop_time_seconds=-1.0
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Negative pit stop time should raise ValueError"
        )