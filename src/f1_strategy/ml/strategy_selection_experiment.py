from dataclasses import dataclass

from sklearn.model_selection import train_test_split

from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.strategy_selector import (
    MLStrategySelector,
    StrategySelectionResult,
)
from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.strategy_result import StrategyResult


@dataclass(frozen=True)
class StrategySelectionExperimentResult:
    """Result of an ML-assisted strategy selection experiment."""

    training_strategies: int
    candidate_strategies: int
    selection: StrategySelectionResult
    actual_fastest_strategy: StrategyResult
    actual_fastest_time: float

    @property
    def selected_actual_time(self) -> float:
        """Return the simulator time of the ML-selected strategy."""

        return self.selection.selected_strategy.total_time_seconds

    @property
    def selection_gap(self) -> float:
        """Return the time gap between ML selection and optimum."""

        return (
            self.selected_actual_time
            - self.actual_fastest_time
        )


class MLStrategySelectionExperiment:
    """Run an ML-assisted race strategy selection experiment."""

    def __init__(
        self,
        number_of_laps: int = 50,
        base_lap_time: float = 90.0,
        test_size: float = 0.2,
        random_state: int = 42,
    ):
        if number_of_laps <= 1:
            raise ValueError(
                "Number of laps must be greater than one"
            )

        if base_lap_time <= 0.0:
            raise ValueError(
                "Base lap time must be greater than zero"
            )

        if not 0.0 < test_size < 1.0:
            raise ValueError(
                "test_size must be between zero and one"
            )

        self._number_of_laps = number_of_laps
        self._base_lap_time = base_lap_time
        self._test_size = test_size
        self._random_state = random_state

    def run(self) -> StrategySelectionExperimentResult:
        """Generate, train, predict, and evaluate strategy selection."""

        generator = StrategyGenerator(
            number_of_laps=self._number_of_laps,
        )

        strategies = (
            generator.generate_two_stint_strategies()
        )

        optimizer = StrategyOptimizer(
            base_lap_time=self._base_lap_time,
        )

        evaluated_strategies = (
            optimizer.evaluate_detailed(
                strategies
            )
        )

        training_strategies, candidate_strategies = (
            train_test_split(
                evaluated_strategies,
                test_size=self._test_size,
                random_state=self._random_state,
            )
        )

        feature_extractor = StrategyFeatureExtractor()

        training_features = [
            feature_extractor.extract(
                strategy.strategy
            )
            for strategy in training_strategies
        ]

        training_targets = [
            strategy.total_time_seconds
            for strategy in training_strategies
        ]

        model = StrategyGradientBoostingModel(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        )

        model.fit(
            features=training_features,
            targets=training_targets,
        )

        selector = MLStrategySelector(
            model=model,
            feature_extractor=feature_extractor,
        )

        selection = selector.select(
            strategies=candidate_strategies,
        )

        actual_fastest_strategy = min(
            candidate_strategies,
            key=lambda strategy: (
                strategy.total_time_seconds
            ),
        )

        return StrategySelectionExperimentResult(
            training_strategies=len(
                training_strategies
            ),
            candidate_strategies=len(
                candidate_strategies
            ),
            selection=selection,
            actual_fastest_strategy=(
                actual_fastest_strategy
            ),
            actual_fastest_time=(
                actual_fastest_strategy.total_time_seconds
            ),
        )


def describe_strategy(
    strategy: StrategyResult,
) -> str:
    """Return a compact human-readable strategy description."""

    stints = " -> ".join(
        (
            f"{stint.tire.compound.label.upper()} "
            f"({stint.number_of_laps} laps)"
        )
        for stint in strategy.strategy.stints
    )

    return stints


def main() -> None:
    """Run and print the V11 ML strategy selection experiment."""

    experiment = MLStrategySelectionExperiment()

    result = experiment.run()

    selected = result.selection.selected_strategy
    actual_fastest = result.actual_fastest_strategy

    print(
        "V11 ML-assisted strategy selection"
    )
    print(
        "================================="
    )
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
        f"Strategy: "
        f"{describe_strategy(selected)}"
    )
    print(
        f"Predicted race time: "
        f"{result.selection.selected_prediction:.3f} s"
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
        f"{describe_strategy(actual_fastest)}"
    )
    print(
        f"Actual race time: "
        f"{result.actual_fastest_time:.3f} s"
    )

    print()

    print("Selection performance")
    print("---------------------")
    print(
        f"Selection gap: "
        f"{result.selection_gap:.3f} s"
    )

    if result.selection_gap == 0.0:
        print(
            "ML selected the simulator-optimal "
            "candidate strategy."
        )
    else:
        print(
            "ML selected a candidate strategy that "
            "was not the simulator-optimal strategy."
        )

    print()

    print("Top 10 ML predictions")
    print("---------------------")

    for rank, prediction in enumerate(
        result.selection.ranked_strategies[:10],
        start=1,
    ):
        print(
            f"{rank:2d}. "
            f"{describe_strategy(prediction.strategy):30s} "
            f"predicted="
            f"{prediction.predicted_time:.3f} s "
            f"actual="
            f"{prediction.strategy.total_time_seconds:.3f} s"
        )


if __name__ == "__main__":
    main()