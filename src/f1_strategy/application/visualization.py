from pathlib import Path

import matplotlib.pyplot as plt

from f1_strategy.ml.race_condition_strategy_selector import (
    RaceConditionStrategySelectionResult,
)


def plot_strategy_predictions(
    selection: RaceConditionStrategySelectionResult,
    output_path: str | Path = "strategy_predictions.png",
    top_n: int = 10,
) -> Path:
    """Plot predicted and actual race times for top ML-ranked strategies."""

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    ranked_strategies = selection.ranked_strategies[:top_n]

    if not ranked_strategies:
        raise ValueError("At least one ranked strategy is required")

    labels = [
        result.strategy.tire_strategy
        for result in ranked_strategies
    ]

    predicted_times = [
        result.predicted_time
        for result in ranked_strategies
    ]

    actual_times = [
        result.strategy.total_time_seconds
        for result in ranked_strategies
    ]

    positions = range(len(ranked_strategies))

    figure, axis = plt.subplots(
        figsize=(12, 6)
    )

    axis.plot(
        positions,
        predicted_times,
        marker="o",
        label="ML prediction",
    )

    axis.plot(
        positions,
        actual_times,
        marker="o",
        label="Actual simulated time",
    )

    axis.set_title(
        "ML Strategy Selection: Predicted vs Actual Race Time"
    )
    axis.set_xlabel("ML-ranked strategy")
    axis.set_ylabel("Race time (seconds)")

    axis.set_xticks(list(positions))
    axis.set_xticklabels(
        labels,
        rotation=45,
        ha="right",
    )

    axis.legend()
    axis.grid(True, alpha=0.3)

    figure.tight_layout()

    output = Path(output_path)
    figure.savefig(output, dpi=150)
    plt.close(figure)

    return output