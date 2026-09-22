from f1_strategy.application import RaceStrategyApplication
from f1_strategy.application.visualization import (
    plot_strategy_predictions,
)


def main() -> None:
    """Run the F1 race strategy application."""

    application = RaceStrategyApplication()
    result = application.run()

    conditions = result.race_condition_summary

    selected_strategy = (
        result.selection.selected_strategy
    )

    fastest_strategy = (
        result.actual_fastest_strategy
    )

    chart_path = plot_strategy_predictions(
        selection=result.selection,
    )

    print()
    print("F1 Race Strategy ML")
    print("===================")

    print()
    print("Race configuration")
    print("------------------")
    print(
        f"Laps: "
        f"{application.config.number_of_laps}"
    )
    print(
        f"Base lap time: "
        f"{application.config.base_lap_time:.1f} s"
    )

    print()
    print("Race conditions")
    print("---------------")
    print(
        f"Green: "
        f"{conditions['green']} laps"
    )
    print(
        f"Yellow: "
        f"{conditions['yellow']} laps"
    )
    print(
        f"VSC: "
        f"{conditions['vsc']} laps"
    )
    print(
        f"Safety Car: "
        f"{conditions['safety_car']} laps"
    )

    print()
    print("Strategy search")
    print("---------------")
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
        f"Strategy: "
        f"{selected_strategy.tire_strategy}"
    )
    print(
        f"Predicted race time: "
        f"{result.selected_predicted_time:.3f} s"
    )
    print(
        f"Actual race time: "
        f"{result.selected_actual_time:.3f} s"
    )

    print()
    print("Actual fastest candidate")
    print("------------------------")
    print(
        f"Strategy: "
        f"{fastest_strategy.tire_strategy}"
    )
    print(
        f"Race time: "
        f"{result.actual_fastest_time:.3f} s"
    )

    print()
    print("Selection performance")
    print("---------------------")
    print(
        f"Gap to fastest candidate: "
        f"{result.selection_gap:.3f} s"
    )

    print()
    print("Visualization")
    print("-------------")
    print(
        f"Strategy prediction chart: "
        f"{chart_path}"
    )