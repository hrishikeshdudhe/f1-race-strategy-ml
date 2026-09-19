from dataclasses import dataclass
from typing import Callable

from sklearn.model_selection import KFold

from f1_strategy.ml.metrics import RegressionMetrics


@dataclass(frozen=True)
class CrossValidationFoldResult:
    """Evaluation result for one cross-validation fold."""

    fold_number: int
    metrics: RegressionMetrics


@dataclass(frozen=True)
class CrossValidationResult:
    """Aggregate evaluation result for a machine learning model."""

    model_name: str
    folds: list[CrossValidationFoldResult]

    @property
    def mean_mae(self) -> float:
        """Return the mean MAE across all folds."""

        return sum(
            fold.metrics.mae
            for fold in self.folds
        ) / len(self.folds)

    @property
    def mean_rmse(self) -> float:
        """Return the mean RMSE across all folds."""

        return sum(
            fold.metrics.rmse
            for fold in self.folds
        ) / len(self.folds)

    @property
    def mean_r2(self) -> float:
        """Return the mean R² across all folds."""

        return sum(
            fold.metrics.r2
            for fold in self.folds
        ) / len(self.folds)

    @property
    def std_mae(self) -> float:
        """Return the population standard deviation of MAE."""

        mean = self.mean_mae

        variance = sum(
            (fold.metrics.mae - mean) ** 2
            for fold in self.folds
        ) / len(self.folds)

        return variance ** 0.5

    @property
    def std_rmse(self) -> float:
        """Return the population standard deviation of RMSE."""

        mean = self.mean_rmse

        variance = sum(
            (fold.metrics.rmse - mean) ** 2
            for fold in self.folds
        ) / len(self.folds)

        return variance ** 0.5

    @property
    def std_r2(self) -> float:
        """Return the population standard deviation of R²."""

        mean = self.mean_r2

        variance = sum(
            (fold.metrics.r2 - mean) ** 2
            for fold in self.folds
        ) / len(self.folds)

        return variance ** 0.5


class ModelCrossValidator:
    """Perform k-fold cross-validation for regression models."""

    def __init__(
        self,
        models: dict[str, Callable[[], object]],
        number_of_folds: int = 5,
        random_state: int = 42,
    ):
        if not models:
            raise ValueError(
                "At least one model is required"
            )

        if number_of_folds < 2:
            raise ValueError(
                "number_of_folds must be at least 2"
            )

        self._models = dict(models)
        self._number_of_folds = number_of_folds
        self._random_state = random_state

    def evaluate(
        self,
        features: list[dict[str, float]],
        targets: list[float],
    ) -> list[CrossValidationResult]:
        """Evaluate all supplied models using k-fold cross-validation."""

        if not features:
            raise ValueError(
                "At least one sample is required"
            )

        if len(features) != len(targets):
            raise ValueError(
                "Features and targets must have "
                "the same length"
            )

        if len(features) < self._number_of_folds:
            raise ValueError(
                "Number of samples must be at least "
                "the number of folds"
            )

        feature_names = list(features[0].keys())

        if not feature_names:
            raise ValueError(
                "At least one feature is required"
            )

        matrix = [
            [
                sample[name]
                for name in feature_names
            ]
            for sample in features
        ]

        splitter = KFold(
            n_splits=self._number_of_folds,
            shuffle=True,
            random_state=self._random_state,
        )

        results = []

        for model_name, model_factory in self._models.items():
            fold_results = []

            for fold_number, (
                train_indices,
                test_indices,
            ) in enumerate(
                splitter.split(matrix),
                start=1,
            ):
                model = model_factory()

                train_features = [
                    features[index]
                    for index in train_indices
                ]

                train_targets = [
                    targets[index]
                    for index in train_indices
                ]

                test_features = [
                    features[index]
                    for index in test_indices
                ]

                test_targets = [
                    targets[index]
                    for index in test_indices
                ]

                model.fit(
                    train_features,
                    train_targets,
                )

                predictions = model.predict(
                    test_features
                )

                metrics = RegressionMetrics(
                    actual=test_targets,
                    predicted=predictions,
                )

                fold_results.append(
                    CrossValidationFoldResult(
                        fold_number=fold_number,
                        metrics=metrics,
                    )
                )

            results.append(
                CrossValidationResult(
                    model_name=model_name,
                    folds=fold_results,
                )
            )

        return results