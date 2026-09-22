from dataclasses import dataclass

from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.strategy_selector import (
    MLStrategySelector,
)
from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.strategy_result import StrategyResult


@dataclass(frozen=True)
class StrategySelectionValidationResult:
    """Result of one ML strategy selection validation run."""

    random_state: int
    training_strategies: int
    candidate_strategies: int
    selected_strategy: StrategyResult
    actual_fastest_strategy: StrategyResult
    predicted_time: float

    @property
    def selected_actual_time(self) -> float:
        """Return the actual time of the selected strategy."""

        return self.selected_strategy.total_time_seconds

    @property
    def actual_fastest_time(self) -> float:
        """Return the actual fastest candidate time."""

        return self.actual_fastest_strategy.total_time_seconds

    @property
    def selection_gap(self) -> float:
        """Return the difference between selected and optimal time."""

        return (
            self.selected_actual_time
            - self.actual_fastest_time
        )

    @property
    def selected_optimal(self) -> bool:
        """Return whether ML selected the actual fastest strategy."""

        return self.selected_actual_time == self.actual_fastest_time


@dataclass(frozen=True)
class StrategySelectionValidationSummary:
    """Aggregate results from multiple validation runs."""

    results: list[StrategySelectionValidationResult]

    @property
    def number_of_runs(self) -> int:
        """Return the number of validation runs."""

        return len(self.results)

    @property
    def exact_optimum_selections(self) -> int:
        """Return the number of runs selecting the exact optimum."""

        return sum(
            result.selected_optimal
            for result in self.results
        )

    @property
    def optimum_selection_rate(self) -> float:
        """Return the percentage of exact optimum selections."""

        if not self.results:
            return 0.0

        return (
            self.exact_optimum_selections
            / self.number_of_runs
            * 100.0
        )

    @property
    def average_selection_gap(self) -> float:
        """Return the average selection gap."""

        if not self.results:
            return 0.0

        return sum(
            result.selection_gap
            for result in self.results
        ) / self.number_of_runs

    @property
    def maximum_selection_gap(self) -> float:
        """Return the largest selection gap."""

        if not self.results:
            return 0.0

        return max(
            result.selection_gap
            for result in self.results
        )

    @property
    def minimum_selection_gap(self) -> float:
        """Return the smallest selection gap."""

        if not self.results:
            return 0.0

        return min(
            result.selection_gap
            for result in self.results
        )


class MLStrategySelectionValidator:
    """Validate ML strategy selection across multiple data splits."""

    def __init__(
        self,
        number_of_laps: int = 50,
        base_lap_time: float = 90.0,
        test_size: float = 0.2,
        random_states: list[int] | None = None,
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
        self._random_states = (
            random_states
            if random_states is not None
            else [1, 2, 3, 4, 5]
        )

    def _generate_evaluated_strategies(
        self,
    ) -> list[StrategyResult]:
        """Generate and evaluate all available strategies."""

        generator = StrategyGenerator(
            number_of_laps=self._number_of_laps,
        )

        strategies = (
            generator.generate_two_stint_strategies()
        )

        optimizer = StrategyOptimizer(
            base_lap_time=self._base_lap_time,
        )

        return optimizer.evaluate_detailed(
            strategies
        )

    def _run_single_validation(
        self,
        evaluated_strategies: list[StrategyResult],
        random_state: int,
    ) -> StrategySelectionValidationResult:
        """Run one train/test strategy selection experiment."""

        from sklearn.model_selection import train_test_split

        training_strategies, candidate_strategies = (
            train_test_split(
                evaluated_strategies,
                test_size=self._test_size,
                random_state=random_state,
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

        return StrategySelectionValidationResult(
            random_state=random_state,
            training_strategies=len(
                training_strategies
            ),
            candidate_strategies=len(
                candidate_strategies
            ),
            selected_strategy=(
                selection.selected_strategy
            ),
            actual_fastest_strategy=(
                actual_fastest_strategy
            ),
            predicted_time=(
                selection.selected_prediction
            ),
        )

    def run(self) -> StrategySelectionValidationSummary:
        """Run all configured validation scenarios."""

        evaluated_strategies = (
            self._generate_evaluated_strategies()
        )

        results = [
            self._run_single_validation(
                evaluated_strategies=evaluated_strategies,
                random_state=random_state,
            )
            for random_state in self._random_states
        ]

        return StrategySelectionValidationSummary(
            results=results
        )


def describe_strategy(
    strategy: StrategyResult,
) -> str:
    """Return a compact human-readable strategy description."""

    return " -> ".join(
        (
            f"{stint.tire.compound.label.upper()} "
            f"({stint.number_of_laps} laps)"
        )
        for stint in strategy.strategy.stints
    )


def main() -> None:
    """Run and print the V11.2 validation experiment."""

    validator = MLStrategySelectionValidator()

    summary = validator.run()

    print(
        "V11.2 ML strategy selection validation"
    )
    print(
        "======================================"
    )
    print()

    print(
        f"Validation runs: "
        f"{summary.number_of_runs}"
    )

    print()

    print("Individual results")
    print("------------------")

    for result in summary.results:
        print(
            f"Run {result.random_state}: "
            f"selected="
            f"{describe_strategy(result.selected_strategy)} | "
            f"optimal="
            f"{describe_strategy(result.actual_fastest_strategy)} | "
            f"gap="
            f"{result.selection_gap:.3f} s"
        )

    print()

    print("Validation summary")
    print("-------------------")

    print(
        f"Exact optimum selections: "
        f"{summary.exact_optimum_selections}/"
        f"{summary.number_of_runs}"
    )

    print(
        f"Exact optimum selection rate: "
        f"{summary.optimum_selection_rate:.1f}%"
    )

    print(
        f"Average selection gap: "
        f"{summary.average_selection_gap:.3f} s"
    )

    print(
        f"Minimum selection gap: "
        f"{summary.minimum_selection_gap:.3f} s"
    )

    print(
        f"Maximum selection gap: "
        f"{summary.maximum_selection_gap:.3f} s"
    )


if __name__ == "__main__":
    main()