from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer


def find_fastest_generated_strategy(
    number_of_laps: int,
    base_lap_time: float,
):
    generator = StrategyGenerator(number_of_laps)

    strategies = generator.generate_two_stint_strategies()

    optimizer = StrategyOptimizer(base_lap_time)

    return optimizer.find_fastest(strategies)


def main() -> None:

    number_of_laps = 6
    base_lap_time = 90.0

    generator = StrategyGenerator(number_of_laps)

    strategies = generator.generate_two_stint_strategies()

    optimizer = StrategyOptimizer(base_lap_time)

    fastest_strategy, fastest_time = optimizer.find_fastest(
        strategies
    )

    print(f"Generated strategies: {len(strategies)}")
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
    print(f"Total race time: {fastest_time:.2f} seconds")


if __name__ == "__main__":
    main()