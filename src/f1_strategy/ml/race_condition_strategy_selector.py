from dataclasses import dataclass

from f1_strategy.ml.race_condition_features import (
    RaceConditionFeatureExtractor,
)
from f1_strategy.simulation.strategy_result import StrategyResult


@dataclass(frozen=True)
class RaceConditionStrategyPrediction:
    """Predicted race time for one strategy under race conditions."""

    strategy: StrategyResult
    predicted_time: float


@dataclass(frozen=True)
class RaceConditionStrategySelectionResult:
    """Result of race-condition-aware ML strategy selection."""

    selected_strategy: StrategyResult
    selected_prediction: float
    ranked_strategies: list[
        RaceConditionStrategyPrediction
    ]


class RaceConditionMLStrategySelector:
    """Select a strategy using strategy and race-condition features."""

    def __init__(
        self,
        model: object,
        feature_extractor: (
            RaceConditionFeatureExtractor | None
        ) = None,
    ):
        self._model = model
        self._feature_extractor = (
            feature_extractor
            if feature_extractor is not None
            else RaceConditionFeatureExtractor()
        )

    def select(
        self,
        strategies: list[StrategyResult],
    ) -> RaceConditionStrategySelectionResult:
        """Select the strategy with the lowest predicted race time."""

        if not strategies:
            raise ValueError(
                "At least one strategy is required"
            )

        features = [
            self._feature_extractor.extract(
                strategy
            )
            for strategy in strategies
        ]

        predictions = self._model.predict(features)

        if len(predictions) != len(strategies):
            raise ValueError(
                "Model must return one prediction for each strategy"
            )

        ranked_strategies = sorted(
            [
                RaceConditionStrategyPrediction(
                    strategy=strategy,
                    predicted_time=prediction,
                )
                for strategy, prediction in zip(
                    strategies,
                    predictions,
                )
            ],
            key=lambda result: result.predicted_time,
        )

        selected = ranked_strategies[0]

        return RaceConditionStrategySelectionResult(
            selected_strategy=selected.strategy,
            selected_prediction=selected.predicted_time,
            ranked_strategies=ranked_strategies,
        )