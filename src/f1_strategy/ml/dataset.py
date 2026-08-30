from f1_strategy.ml.features import StrategyFeatureExtractor
from f1_strategy.simulation.strategy_result import StrategyResult


class StrategyMLDataset:
    """Represent strategy simulation results as an ML dataset."""

    def __init__(
        self,
        results: list[StrategyResult],
    ):
        self.results = list(results)
        self.feature_extractor = StrategyFeatureExtractor()

    def feature_names(self) -> list[str]:
        """Return the names of all ML features."""

        if not self.results:
            return []

        features = self.feature_extractor.extract(
            self.results[0].strategy
        )

        return list(features.keys())

    def features(self) -> list[dict[str, float]]:
        """Return feature dictionaries for all results."""

        return [
            self.feature_extractor.extract(
                result.strategy
            )
            for result in self.results
        ]

    def targets(self) -> list[float]:
        """Return actual simulated race times."""

        return [
            float(result.total_time_seconds)
            for result in self.results
        ]

    def __len__(self) -> int:
        """Return the number of samples."""

        return len(self.results)