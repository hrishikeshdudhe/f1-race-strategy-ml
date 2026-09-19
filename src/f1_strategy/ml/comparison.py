from dataclasses import dataclass

from f1_strategy.ml.metrics import RegressionMetrics


@dataclass(frozen=True)
class ModelComparisonResult:
    """Evaluation result for a single machine learning model."""

    model_name: str
    metrics: RegressionMetrics


class ModelComparator:
    """Compare multiple regression models on the same dataset."""

    def __init__(
        self,
        models: dict[str, object],
    ):
        if not models:
            raise ValueError(
                "At least one model is required"
            )

        self._models = dict(models)

    def evaluate(
        self,
        train_features: list[dict[str, float]],
        train_targets: list[float],
        test_features: list[dict[str, float]],
        test_targets: list[float],
    ) -> list[ModelComparisonResult]:
        """Train and evaluate all supplied models."""

        if not train_features:
            raise ValueError(
                "At least one training sample is required"
            )

        if not test_features:
            raise ValueError(
                "At least one test sample is required"
            )

        if len(train_features) != len(train_targets):
            raise ValueError(
                "Training features and targets must have "
                "the same length"
            )

        if len(test_features) != len(test_targets):
            raise ValueError(
                "Test features and targets must have "
                "the same length"
            )

        results = []

        for model_name, model in self._models.items():
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

            results.append(
                ModelComparisonResult(
                    model_name=model_name,
                    metrics=metrics,
                )
            )

        return results