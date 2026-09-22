from f1_strategy.application import RaceStrategyApplication


def main() -> None:
    """Run the F1 race strategy application."""

    application = RaceStrategyApplication()
    result = application.run()

    print()
    print("F1 Race Strategy ML")
    print("===================")
    print()
    print(
        f"Training strategies: "
        f"{result.training_strategies}"
    )
    print(
        f"Candidate strategies: "
        f"{result.candidate_strategies}"
    )
    print()
    print("ML-selected strategy")
    print("--------------------")
    print(
        f"Actual race time: "
        f"{result.selected_actual_time:.3f} s"
    )
    print()
    print("Actual fastest candidate")
    print("------------------------")
    print(
        f"Race time: "
        f"{result.actual_fastest_time:.3f} s"
    )
    print()
    print("Selection performance")
    print("---------------------")
    print(
        f"Gap: "
        f"{result.selection_gap:.3f} s"
    )
