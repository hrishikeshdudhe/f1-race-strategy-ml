from sklearn.model_selection import train_test_split

from f1_strategy.ml.dataset import StrategyMLDataset
from f1_strategy.ml.metrics import RegressionMetrics
from f1_strategy.ml.model import StrategyRegressionModel
from f1_strategy.ml.prediction import PredictionError
from f1_strategy.simulation.strategy_result import StrategyResult


class StrategyMLPipeline:
    """Train and evaluate a regression model for race strategy prediction."""

    def __init__(
        self,
        test_size: float = 0.2,
        random_state: int = 42,
    ):
        if not 0.0 < test_size < 1.0:
            raise ValueError(
                "test_size must be between 0 and 1"
            )

        self.test_size = test_size
        self.random_state = random_state
        self.model = StrategyRegressionModel()
        self._is_fitted = False
        self._train_features = []
        self._train_targets = []
        self._test_features = []
        self._test_targets = []

    def prepare_dataset(
        self,
        results: list[StrategyResult],
    ) -> StrategyMLDataset:
        """Create an ML dataset from simulation results."""

        if not results:
            raise ValueError(
                "At least one result is required"
            )

        return StrategyMLDataset(results)

    def train(
        self,
        results: list[StrategyResult],
    ) -> None:
        """Split the data and train the regression model."""

        dataset = self.prepare_dataset(results)

        features = dataset.features()
        targets = dataset.targets()

        if len(features) < 2:
            raise ValueError(
                "At least two samples are required "
                "for train/test splitting"
            )

        (
            train_features,
            test_features,
            train_targets,
            test_targets,
        ) = train_test_split(
            features,
            targets,
            test_size=self.test_size,
            random_state=self.random_state,
        )

        self.model.fit(
            train_features,
            train_targets,
        )

        self._train_features = train_features
        self._train_targets = train_targets
        self._test_features = test_features
        self._test_targets = test_targets
        self._is_fitted = True

    def predict(
        self,
        results: list[StrategyResult],
    ) -> list[float]:
        """Predict race times for strategy results."""

        if not self._is_fitted:
            raise RuntimeError(
                "Pipeline must be trained before prediction"
            )

        dataset = self.prepare_dataset(results)

        return self.model.predict(
            dataset.features()
        )

    def evaluate(self) -> RegressionMetrics:
        """Evaluate the model using the held-out test set."""

        if not self._is_fitted:
            raise RuntimeError(
                "Pipeline must be trained before evaluation"
            )

        predictions = self.model.predict(
            self._test_features
        )

        return RegressionMetrics(
            actual=self._test_targets,
            predicted=predictions,
        )

    def prediction_errors(
        self,
    ) -> list[PredictionError]:
        """Return prediction errors for the held-out test set."""

        if not self._is_fitted:
            raise RuntimeError(
                "Pipeline must be trained before "
                "prediction error analysis"
            )

        predictions = self.model.predict(
            self._test_features
        )

        return [
            PredictionError(
                actual=actual,
                predicted=predicted,
            )
            for actual, predicted in zip(
                self._test_targets,
                predictions,
            )
        ]

    @property
    def train_features(
        self,
    ) -> list[dict[str, float]]:
        """Return the training features."""

        return list(self._train_features)

    @property
    def train_targets(
        self,
    ) -> list[float]:
        """Return the training targets."""

        return list(self._train_targets)

    @property
    def test_features(
        self,
    ) -> list[dict[str, float]]:
        """Return the held-out test features."""

        return list(self._test_features)

    @property
    def test_targets(
        self,
    ) -> list[float]:
        """Return the held-out test targets."""

        return list(self._test_targets)