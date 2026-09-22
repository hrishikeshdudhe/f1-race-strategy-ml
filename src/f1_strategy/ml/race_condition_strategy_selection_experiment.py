from dataclasses import dataclass

from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.race_condition_features import (
    RaceConditionFeatureExtractor,
)
from f1_strategy.ml.race_condition_strategy_selector import (
    RaceConditionMLStrategySelector,
    RaceConditionStrategySelectionResult,
)
from f1_strategy.simulation.generator import StrategyGenerator
from f1_strategy.simulation.optimizer import StrategyOptimizer
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.strategy_result import StrategyResult


@dataclass(frozen=True)
class RaceConditionStrategySelectionExperimentResult:
    """Result of one race-condition-aware selection experiment."""

    training_strategies: int
    candidate_strategies: int
    selection: RaceConditionStrategySelectionResult
    actual_fastest_strategy: StrategyResult
    actual_fastest_time: float

    @property
    def selected_actual_time(self) -> float:
        """Return the simulator time of the selected strategy."""

        return self.selection.selected_strategy.total_time_seconds

    @property
    def selection_gap(self) -> float:
        """Return the gap between selected and optimal time."""

        return (
            self.selected_actual_time
            - self.actual_fastest_time
        )


class RaceConditionStrategySelectionExperiment:
    """Run ML strategy selection under race conditions."""

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

    def _create_race_condition_schedule(
        self,
    ) -> RaceConditionSchedule:
        """Create a deterministic mixed-condition race schedule."""

        schedule = RaceConditionSchedule(
            number_of_laps=self._number_of_laps,
            default_condition=RaceCondition.GREEN,
        )

        yellow_start = max(
            1,
            self._number_of_laps // 5,
        )
        yellow_end = min(
            self._number_of_laps,
            yellow_start + 2,
        )

        vsc_start = max(
            1,
            self._number_of_laps // 2,
        )
        vsc_end = min(
            self._number_of_laps,
            vsc_start + 2,
        )

        safety_car_start = max(
            1,
            (self._number_of_laps * 3) // 4,
        )
        safety_car_end = min(
            self._number_of_laps,
            safety_car_start + 2,
        )

        schedule.set_condition(
            start_lap=yellow_start,
            end_lap=yellow_end,
            condition=RaceCondition.YELLOW,
        )

        schedule.set_condition(
            start_lap=vsc_start,
            end_lap=vsc_end,
            condition=RaceCondition.VSC,
        )

        schedule.set_condition(
            start_lap=safety_car_start,
            end_lap=safety_car_end,
            condition=RaceCondition.SAFETY_CAR,
        )

        return schedule

    def run(
        self,
    ) -> RaceConditionStrategySelectionExperimentResult:
        """Generate, train, predict, and evaluate strategies."""

        generator = StrategyGenerator(
            number_of_laps=self._number_of_laps,
        )

        strategies = (
            generator.generate_two_stint_strategies()
        )

        schedule = self._create_race_condition_schedule()

        optimizer = StrategyOptimizer(
            base_lap_time=self._base_lap_time,
            race_condition_schedule=schedule,
        )

        evaluated_strategies = (
            optimizer.evaluate_detailed(
                strategies
            )
        )

        from sklearn.model_selection import train_test_split

        training_strategies, candidate_strategies = (
            train_test_split(
                evaluated_strategies,
                test_size=self._test_size,
                random_state=self._random_state,
            )
        )

        feature_extractor = RaceConditionFeatureExtractor()

        training_features = [
            feature_extractor.extract(
                strategy
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

        selector = RaceConditionMLStrategySelector(
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

        return RaceConditionStrategySelectionExperimentResult(
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

    return " -> ".join(
        (
            f"{stint.tire.compound.label.upper()} "
            f"({stint.number_of_laps} laps)"
        )
        for stint in strategy.strategy.stints
    )


def main() -> None:
    """Run and print the V11.3 experiment."""

    experiment = RaceConditionStrategySelectionExperiment()

    result = experiment.run()

    selected = result.selection.selected_strategy
    actual_fastest = result.actual_fastest_strategy

    print(
        "V11.3 Race-condition-aware ML strategy selection"
    )
    print(
        "==============================================="
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

    print("Race conditions")
    print("---------------")
    print(
        f"Green laps: "
        f"{selected.green_laps}"
    )
    print(
        f"Yellow laps: "
        f"{selected.yellow_laps}"
    )
    print(
        f"VSC laps: "
        f"{selected.vsc_laps}"
    )
    print(
        f"Safety Car laps: "
        f"{selected.safety_car_laps}"
    )
    print(
        f"Race-condition delay: "
        f"{selected.race_condition_delay_seconds:.3f} s"
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