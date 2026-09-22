from dataclasses import dataclass

from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.simulation.strategy_result import StrategyResult


@dataclass(frozen=True)
class StrategyPrediction:
    """Predicted race time for one strategy."""

    strategy: StrategyResult
    predicted_time: float


@dataclass(frozen=True)
class StrategySelectionResult:
    """Result of selecting a strategy using a machine learning model."""

    selected_strategy: StrategyResult
    selected_prediction: float
    ranked_strategies: list[StrategyPrediction]


class MLStrategySelector:
    """Select a race strategy using a trained machine learning model."""

    def __init__(
        self,
        model: object,
        feature_extractor: StrategyFeatureExtractor | None = None,
    ):
        self._model = model
        self._feature_extractor = (
            feature_extractor
            if feature_extractor is not None
            else StrategyFeatureExtractor()
        )

    def select(
        self,
        strategies: list[StrategyResult],
    ) -> StrategySelectionResult:
        """Select the strategy with the lowest predicted race time."""

        if not strategies:
            raise ValueError(
                "At least one strategy is required"
            )

        features = [
            self._feature_extractor.extract(
                strategy.strategy
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
                StrategyPrediction(
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

        return StrategySelectionResult(
            selected_strategy=selected.strategy,
            selected_prediction=selected.predicted_time,
            ranked_strategies=ranked_strategies,
        )