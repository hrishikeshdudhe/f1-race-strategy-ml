from f1_strategy.simulation.run_strategy_search import (
    find_fastest_generated_strategy,
)


def test_generated_strategy_search_returns_strategy():

    strategy, race_time = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert strategy is not None
    assert race_time > 0


def test_generated_strategy_search_covers_entire_race():

    strategy, _ = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert strategy.total_laps() == 6


def test_generated_strategy_search_finds_two_stints():

    strategy, _ = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert len(strategy.stints) == 2


def test_generated_strategy_search_uses_generated_strategies():

    strategy, race_time = find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    assert race_time == strategy.total_time_seconds(90.0)