from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.strategy_results import (
    StrategyResults,
)


class StrategyDatasetGenerator:

    def __init__(
        self,
        number_of_laps: int,
        base_lap_time: float,
        initial_fuel_mass_kg: float | None = None,
        fuel_consumption_per_lap_kg: float | None = None,
        race_condition_schedule: (
            RaceConditionSchedule | None
        ) = None,
    ):
        if number_of_laps <= 0:
            raise ValueError(
                "Number of laps must be positive"
            )

        if base_lap_time <= 0:
            raise ValueError(
                "Base lap time must be positive"
            )

        self.number_of_laps = number_of_laps
        self.base_lap_time = base_lap_time
        self.initial_fuel_mass_kg = (
            initial_fuel_mass_kg
        )
        self.fuel_consumption_per_lap_kg = (
            fuel_consumption_per_lap_kg
        )
        self.race_condition_schedule = (
            race_condition_schedule
        )

    def generate_strategies(self):
        generator = StrategyGenerator(
            number_of_laps=self.number_of_laps,
            initial_fuel_mass_kg=(
                self.initial_fuel_mass_kg
            ),
            fuel_consumption_per_lap_kg=(
                self.fuel_consumption_per_lap_kg
            ),
        )

        return generator.generate_two_stint_strategies()

    def evaluate_strategies(self):
        strategies = self.generate_strategies()

        optimizer = StrategyOptimizer(
            base_lap_time=self.base_lap_time,
            race_condition_schedule=(
                self.race_condition_schedule
            ),
        )

        return optimizer.rank_strategies_collection(
            strategies
        )

    def export_csv(
        self,
        file_path: str,
    ) -> None:
        results = self.evaluate_strategies()

        results.export_csv(file_path)

    def configuration(self) -> dict:
        return {
            "number_of_laps": self.number_of_laps,
            "base_lap_time": self.base_lap_time,
            "initial_fuel_mass_kg": (
                self.initial_fuel_mass_kg
            ),
            "fuel_consumption_per_lap_kg": (
                self.fuel_consumption_per_lap_kg
            ),
            "race_condition_schedule": (
                self.race_condition_schedule
            ),
        }

    @classmethod
    def from_configuration(
        cls,
        configuration: dict,
    ) -> "StrategyDatasetGenerator":
        return cls(
            number_of_laps=configuration[
                "number_of_laps"
            ],
            base_lap_time=configuration[
                "base_lap_time"
            ],
            initial_fuel_mass_kg=configuration.get(
                "initial_fuel_mass_kg"
            ),
            fuel_consumption_per_lap_kg=(
                configuration.get(
                    "fuel_consumption_per_lap_kg"
                )
            ),
            race_condition_schedule=(
                configuration.get(
                    "race_condition_schedule"
                )
            ),
        )


class MultiConfigurationDataset:

    def __init__(
        self,
        configurations: list[dict],
    ):
        if not configurations:
            raise ValueError(
                "At least one configuration is required"
            )

        self.configurations = configurations

    def generate_results(self) -> list[StrategyResults]:
        results = []

        for configuration in self.configurations:
            generator = (
                StrategyDatasetGenerator.from_configuration(
                    configuration
                )
            )

            results.append(
                generator.evaluate_strategies()
            )

        return results

    def total_strategy_count(self) -> int:
        return sum(
            len(results)
            for results in self.generate_results()
        )

    def _race_condition_description(
        self,
        schedule: RaceConditionSchedule | None,
        number_of_laps: int,
    ) -> str:
        if schedule is None:
            return "normal"

        conditions = []

        for lap in range(
            1,
            number_of_laps + 1,
        ):
            condition = schedule.condition_for_lap(
                lap
            )

            if condition.label != "green":
                conditions.append(
                    f"{condition.label}:{lap}"
                )

        if not conditions:
            return "normal"

        return ";".join(conditions)

    def export_csv(
        self,
        file_path: str,
    ) -> None:
        all_results = self.generate_results()

        if not all_results:
            return

        import csv

        fieldnames = [
            "configuration_id",
            "number_of_laps",
            "base_lap_time",
            "race_condition",
            "race_condition_laps",
            "green_laps",
            "yellow_laps",
            "vsc_laps",
            "safety_car_laps",
            "race_condition_delay_seconds",
            "race_condition_summary",
            "rank",
            "total_time_seconds",
            "time_delta_seconds",
            "time_gap_percentage",
            "time_gap_to_next_seconds",
            "average_lap_time_seconds",
            "total_laps",
            "number_of_stints",
            "number_of_pit_stops",
            "pit_stop_time_seconds",
            "tire_strategy",
            "stint_laps",
        ]

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for configuration_id, results in enumerate(
                all_results
            ):
                configuration = (
                    self.configurations[
                        configuration_id
                    ]
                )

                schedule = configuration.get(
                    "race_condition_schedule"
                )

                race_condition = (
                    self._race_condition_description(
                        schedule,
                        configuration[
                            "number_of_laps"
                        ],
                    )
                )

                for result in results:
                    writer.writerow(
                        {
                            "configuration_id": (
                                configuration_id
                            ),
                            "number_of_laps": (
                                configuration[
                                    "number_of_laps"
                                ]
                            ),
                            "base_lap_time": (
                                configuration[
                                    "base_lap_time"
                                ]
                            ),
                            "race_condition": (
                                race_condition
                            ),
                            "race_condition_laps": (
                                result.race_condition_laps
                            ),
                            "green_laps": (
                                result.green_laps
                            ),
                            "yellow_laps": (
                                result.yellow_laps
                            ),
                            "vsc_laps": (
                                result.vsc_laps
                            ),
                            "safety_car_laps": (
                                result.safety_car_laps
                            ),
                            "race_condition_delay_seconds": (
                                result.race_condition_delay_seconds
                            ),
                            "race_condition_summary": (
                                result.race_condition_summary
                            ),
                            "rank": result.rank,
                            "total_time_seconds": (
                                result.total_time_seconds
                            ),
                            "time_delta_seconds": (
                                result.time_delta_seconds
                            ),
                            "time_gap_percentage": (
                                result.time_gap_percentage
                            ),
                            "time_gap_to_next_seconds": (
                                result.time_gap_to_next_seconds
                            ),
                            "average_lap_time_seconds": (
                                result.average_lap_time_seconds
                            ),
                            "total_laps": (
                                result.total_laps
                            ),
                            "number_of_stints": (
                                result.number_of_stints
                            ),
                            "number_of_pit_stops": (
                                result.number_of_pit_stops
                            ),
                            "pit_stop_time_seconds": (
                                result.pit_stop_time_seconds
                            ),
                            "tire_strategy": (
                                result.tire_strategy
                            ),
                            "stint_laps": ",".join(
                                str(laps)
                                for laps in result.stint_laps
                            ),
                        }
                    )