from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)


def find_fastest_generated_strategy(
    number_of_laps: int,
    base_lap_time: float,
    initial_fuel_mass_kg: float | None = None,
    fuel_consumption_per_lap_kg: float = 2.0,
    race_condition_schedule: RaceConditionSchedule | None = None,
):

    generator = StrategyGenerator(
        number_of_laps=number_of_laps,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        fuel_consumption_per_lap_kg=(
            fuel_consumption_per_lap_kg
        ),
    )

    strategies = (
        generator.generate_two_stint_strategies()
    )

    optimizer = StrategyOptimizer(
        base_lap_time=base_lap_time,
        race_condition_schedule=race_condition_schedule,
    )

    return optimizer.find_fastest(strategies)


def main() -> None:

    number_of_laps = 6
    base_lap_time = 90.0
    initial_fuel_mass_kg = 100.0
    fuel_consumption_per_lap_kg = 2.0

    schedule = RaceConditionSchedule(
        number_of_laps
    )

    schedule.set_condition(
        start_lap=3,
        end_lap=3,
        condition=RaceCondition.VSC,
    )

    generator = StrategyGenerator(
        number_of_laps=number_of_laps,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        fuel_consumption_per_lap_kg=(
            fuel_consumption_per_lap_kg
        ),
    )

    strategies = (
        generator.generate_two_stint_strategies()
    )

    optimizer = StrategyOptimizer(
        base_lap_time=base_lap_time,
        race_condition_schedule=schedule,
    )

    fastest_strategy, fastest_time = (
        optimizer.find_fastest(strategies)
    )

    print(
        f"Generated strategies: {len(strategies)}"
    )

    print()

    print("Race conditions:")

    for lap in range(1, number_of_laps + 1):

        condition = schedule.condition_for_lap(lap)

        print(
            f"  Lap {lap}: "
            f"{condition.label.upper()}"
        )

    print()

    print("Fastest strategy:")

    for index, stint in enumerate(
        fastest_strategy.stints,
        start=1,
    ):

        print(
            f"  Stint {index}: "
            f"{stint.tire.compound.label.upper()} "
            f"- {stint.number_of_laps} laps"
        )

    print()

    print(
        f"Total race time: "
        f"{fastest_time:.2f} seconds"
    )

    if fastest_strategy.fuel is not None:

        print(
            f"Remaining fuel: "
            f"{fastest_strategy.fuel.remaining_fuel_kg():.2f} kg"
        )


if __name__ == "__main__":
    main()