from dataclasses import dataclass

from sklearn.model_selection import train_test_split

from f1_strategy.application.config import (
    RaceStrategyApplicationConfig,
)
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
class RaceStrategyApplicationResult:
    """Result of one complete race strategy application run."""

    training_strategies: int
    candidate_strategies: int
    selection: RaceConditionStrategySelectionResult
    actual_fastest_strategy: StrategyResult
    race_condition_schedule: RaceConditionSchedule

    @property
    def selected_actual_time(self) -> float:
        """Return the simulated time of the ML-selected strategy."""

        return self.selection.selected_strategy.total_time_seconds

    @property
    def selected_predicted_time(self) -> float:
        """Return the ML-predicted time of the selected strategy."""

        return self.selection.selected_prediction

    @property
    def actual_fastest_time(self) -> float:
        """Return the simulated time of the fastest candidate."""

        return self.actual_fastest_strategy.total_time_seconds

    @property
    def selection_gap(self) -> float:
        """Return the time gap between selected and fastest strategy."""

        return (
            self.selected_actual_time
            - self.actual_fastest_time
        )

    @property
    def race_condition_summary(self) -> dict[str, int]:
        """Return the number of laps under each race condition."""

        summary = {
            "green": 0,
            "yellow": 0,
            "vsc": 0,
            "safety_car": 0,
        }

        for lap in range(
            1,
            self.race_condition_schedule.number_of_laps + 1,
        ):
            condition = (
                self.race_condition_schedule
                .condition_for_lap(lap)
            )

            summary[condition.label] += 1

        return summary


class RaceStrategyApplication:
    """Run the complete F1 race strategy ML workflow."""

    def __init__(
        self,
        config: RaceStrategyApplicationConfig | None = None,
    ):
        self.config = (
            config
            if config is not None
            else RaceStrategyApplicationConfig()
        )

    def _create_race_condition_schedule(
        self,
    ) -> RaceConditionSchedule:
        """Create the deterministic mixed-condition race schedule."""

        schedule = RaceConditionSchedule(
            number_of_laps=self.config.number_of_laps,
            default_condition=RaceCondition.GREEN,
        )

        yellow_start = max(
            1,
            self.config.number_of_laps // 5,
        )
        yellow_end = min(
            self.config.number_of_laps,
            yellow_start + 2,
        )

        vsc_start = max(
            1,
            self.config.number_of_laps // 2,
        )
        vsc_end = min(
            self.config.number_of_laps,
            vsc_start + 2,
        )

        safety_car_start = max(
            1,
            (self.config.number_of_laps * 3) // 4,
        )
        safety_car_end = min(
            self.config.number_of_laps,
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

    def _generate_strategies(self):
        """Generate candidate race strategies."""

        generator = StrategyGenerator(
            number_of_laps=self.config.number_of_laps,
            pit_stop_time_seconds=(
                self.config.pit_stop_time_seconds
            ),
        )

        return generator.generate_two_stint_strategies()

    def _evaluate_strategies(
        self,
        strategies,
        schedule: RaceConditionSchedule,
    ) -> list[StrategyResult]:
        """Simulate strategies under the configured race conditions."""

        optimizer = StrategyOptimizer(
            base_lap_time=self.config.base_lap_time,
            race_condition_schedule=schedule,
        )

        return optimizer.evaluate_detailed(strategies)

    def _split_strategies(
        self,
        strategies: list[StrategyResult],
    ) -> tuple[
        list[StrategyResult],
        list[StrategyResult],
    ]:
        """Split strategies into training and candidate sets."""

        return train_test_split(
            strategies,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
        )

    def _train_model(
        self,
        training_strategies: list[StrategyResult],
    ) -> tuple[
        StrategyGradientBoostingModel,
        RaceConditionFeatureExtractor,
    ]:
        """Train the race-condition-aware gradient boosting model."""

        feature_extractor = RaceConditionFeatureExtractor()

        training_features = [
            feature_extractor.extract(strategy)
            for strategy in training_strategies
        ]

        training_targets = [
            strategy.total_time_seconds
            for strategy in training_strategies
        ]

        model = StrategyGradientBoostingModel(
            n_estimators=self.config.n_estimators,
            learning_rate=self.config.learning_rate,
            max_depth=self.config.max_depth,
            random_state=self.config.random_state,
        )

        model.fit(
            features=training_features,
            targets=training_targets,
        )

        return model, feature_extractor

    def _select_strategy(
        self,
        model: StrategyGradientBoostingModel,
        feature_extractor: RaceConditionFeatureExtractor,
        candidate_strategies: list[StrategyResult],
    ) -> RaceConditionStrategySelectionResult:
        """Select a strategy using ML predictions."""

        selector = RaceConditionMLStrategySelector(
            model=model,
            feature_extractor=feature_extractor,
        )

        return selector.select(
            strategies=candidate_strategies,
        )

    def run(self) -> RaceStrategyApplicationResult:
        """Run the complete strategy generation, simulation, and ML workflow."""

        schedule = self._create_race_condition_schedule()

        strategies = self._generate_strategies()

        if not strategies:
            raise RuntimeError(
                "Strategy generation produced no valid strategies"
            )

        evaluated_strategies = self._evaluate_strategies(
            strategies,
            schedule,
        )

        training_strategies, candidate_strategies = (
            self._split_strategies(
                evaluated_strategies
            )
        )

        model, feature_extractor = self._train_model(
            training_strategies
        )

        selection = self._select_strategy(
            model=model,
            feature_extractor=feature_extractor,
            candidate_strategies=candidate_strategies,
        )

        actual_fastest_strategy = min(
            candidate_strategies,
            key=lambda strategy: (
                strategy.total_time_seconds
            ),
        )

        return RaceStrategyApplicationResult(
            training_strategies=len(
                training_strategies
            ),
            candidate_strategies=len(
                candidate_strategies
            ),
            selection=selection,
            actual_fastest_strategy=actual_fastest_strategy,
            race_condition_schedule=schedule,
        )