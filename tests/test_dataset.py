import pytest

from f1_strategy.simulation.dataset import (
    MultiConfigurationDataset,
    StrategyDatasetGenerator,
)
from f1_strategy.simulation.race_condition import (
    RaceCondition,
)
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)


def test_dataset_generator_creates_strategies():
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    strategies = generator.generate_strategies()

    assert len(strategies) > 0


def test_dataset_generator_strategies_cover_race():
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    strategies = generator.generate_strategies()

    for strategy in strategies:
        assert strategy.total_laps() == 6


def test_dataset_generator_evaluates_strategies():
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    results = generator.evaluate_strategies()

    assert len(results) > 0


def test_dataset_generator_results_are_ranked():
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    results = generator.evaluate_strategies()

    assert results[0].rank == 1


def test_dataset_generator_fastest_result_is_first():
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    results = generator.evaluate_strategies()

    for index in range(1, len(results)):
        assert (
            results[index - 1].total_time_seconds
            <= results[index].total_time_seconds
        )


def test_dataset_generator_can_export_csv(tmp_path):
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    file_path = tmp_path / "strategy_dataset.csv"

    generator.export_csv(str(file_path))

    assert file_path.exists()


def test_dataset_generator_export_contains_data(tmp_path):
    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    file_path = tmp_path / "strategy_dataset.csv"

    generator.export_csv(str(file_path))

    lines = file_path.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) > 1


def test_dataset_generator_rejects_invalid_lap_count():
    with pytest.raises(ValueError):
        StrategyDatasetGenerator(
            number_of_laps=0,
            base_lap_time=90.0,
        )


def test_dataset_generator_rejects_negative_lap_count():
    with pytest.raises(ValueError):
        StrategyDatasetGenerator(
            number_of_laps=-5,
            base_lap_time=90.0,
        )


def test_dataset_generator_rejects_invalid_base_lap_time():
    with pytest.raises(ValueError):
        StrategyDatasetGenerator(
            number_of_laps=6,
            base_lap_time=0.0,
        )


def test_dataset_generator_rejects_negative_base_lap_time():
    with pytest.raises(ValueError):
        StrategyDatasetGenerator(
            number_of_laps=6,
            base_lap_time=-90.0,
        )


def test_dataset_generator_stores_configuration():
    generator = StrategyDatasetGenerator(
        number_of_laps=10,
        base_lap_time=92.5,
        initial_fuel_mass_kg=100.0,
        fuel_consumption_per_lap_kg=2.0,
    )

    configuration = generator.configuration()

    assert configuration == {
        "number_of_laps": 10,
        "base_lap_time": 92.5,
        "initial_fuel_mass_kg": 100.0,
        "fuel_consumption_per_lap_kg": 2.0,
        "race_condition_schedule": None,
    }


def test_dataset_generator_supports_different_race_lengths():
    short_race = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    longer_race = StrategyDatasetGenerator(
        number_of_laps=10,
        base_lap_time=90.0,
    )

    short_strategies = (
        short_race.generate_strategies()
    )

    long_strategies = (
        longer_race.generate_strategies()
    )

    for strategy in short_strategies:
        assert strategy.total_laps() == 6

    for strategy in long_strategies:
        assert strategy.total_laps() == 10


def test_generator_can_be_created_from_configuration():
    configuration = {
        "number_of_laps": 8,
        "base_lap_time": 91.5,
        "initial_fuel_mass_kg": 100.0,
        "fuel_consumption_per_lap_kg": 2.0,
        "race_condition_schedule": None,
    }

    generator = (
        StrategyDatasetGenerator.from_configuration(
            configuration
        )
    )

    assert generator.configuration() == configuration


def test_dataset_generator_accepts_race_condition_schedule():
    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    assert (
        generator.race_condition_schedule
        is schedule
    )


def test_dataset_generator_applies_race_condition():
    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    normal_generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
    )

    affected_generator = StrategyDatasetGenerator(
        number_of_laps=6,
        base_lap_time=90.0,
        race_condition_schedule=schedule,
    )

    normal_results = (
        normal_generator.evaluate_strategies()
    )

    affected_results = (
        affected_generator.evaluate_strategies()
    )

    assert (
        affected_results[0].total_time_seconds
        > normal_results[0].total_time_seconds
    )


def test_multi_configuration_dataset_accepts_configurations():
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    assert len(dataset.configurations) == 2


def test_multi_configuration_dataset_generates_results():
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    results = dataset.generate_results()

    assert len(results) == 2


def test_multi_configuration_dataset_results_cover_configured_races():
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    results = dataset.generate_results()

    for result in results[0]:
        assert result.total_laps == 6

    for result in results[1]:
        assert result.total_laps == 8


def test_multi_configuration_dataset_counts_all_strategies():
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    assert dataset.total_strategy_count() > 0


def test_multi_configuration_dataset_can_export_csv(
    tmp_path,
):
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    file_path = tmp_path / "multi_dataset.csv"

    dataset.export_csv(str(file_path))

    assert file_path.exists()


def test_multi_configuration_dataset_export_contains_configuration_id(
    tmp_path,
):
    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
        },
        {
            "number_of_laps": 8,
            "base_lap_time": 91.5,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    file_path = tmp_path / "multi_dataset.csv"

    dataset.export_csv(str(file_path))

    content = file_path.read_text(
        encoding="utf-8"
    )

    assert "configuration_id" in content
    assert "number_of_laps" in content
    assert "base_lap_time" in content


def test_multi_configuration_dataset_exports_race_condition(
    tmp_path,
):
    schedule = RaceConditionSchedule(6)

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    configurations = [
        {
            "number_of_laps": 6,
            "base_lap_time": 90.0,
            "race_condition_schedule": schedule,
        },
    ]

    dataset = MultiConfigurationDataset(
        configurations
    )

    file_path = tmp_path / "race_condition_dataset.csv"

    dataset.export_csv(str(file_path))

    content = file_path.read_text(
        encoding="utf-8"
    )

    assert "race_condition" in content
    assert "vsc:3" in content