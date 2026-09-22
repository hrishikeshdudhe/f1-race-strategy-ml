from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.simulation.strategy_result import StrategyResult


class RaceConditionFeatureExtractor:
    """Extract strategy and race-condition features for ML."""

    def __init__(
        self,
        strategy_feature_extractor: StrategyFeatureExtractor | None = None,
    ):
        self._strategy_feature_extractor = (
            strategy_feature_extractor
            if strategy_feature_extractor is not None
            else StrategyFeatureExtractor()
        )

    def extract(
        self,
        strategy_result: StrategyResult,
    ) -> dict[str, float]:
        """Extract strategy and race-condition features."""

        features = self._strategy_feature_extractor.extract(
            strategy_result.strategy
        )

        features.update(
            {
                "green_laps": float(
                    strategy_result.green_laps
                ),
                "yellow_laps": float(
                    strategy_result.yellow_laps
                ),
                "vsc_laps": float(
                    strategy_result.vsc_laps
                ),
                "safety_car_laps": float(
                    strategy_result.safety_car_laps
                ),
                "race_condition_laps": float(
                    strategy_result.race_condition_laps
                ),
                "race_condition_delay_seconds": float(
                    strategy_result.race_condition_delay_seconds
                ),
            }
        )

        return features