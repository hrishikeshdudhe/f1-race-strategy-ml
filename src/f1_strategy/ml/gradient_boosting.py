from sklearn.ensemble import GradientBoostingRegressor


class StrategyGradientBoostingModel:
    """Gradient boosting regression model for predicting race strategy time."""

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
        random_state: int = 42,
    ):
        if n_estimators <= 0:
            raise ValueError(
                "n_estimators must be greater than zero"
            )

        if learning_rate <= 0.0:
            raise ValueError(
                "learning_rate must be greater than zero"
            )

        if max_depth <= 0:
            raise ValueError(
                "max_depth must be greater than zero"
            )

        self._model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=random_state,
        )

        self._is_fitted = False

    def fit(
        self,
        features: list[dict[str, float]],
        targets: list[float],
    ) -> None:
        """Train the gradient boosting model."""

        if not features:
            raise ValueError(
                "At least one training sample is required"
            )

        if len(features) != len(targets):
            raise ValueError(
                "Features and targets must have the same length"
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

        self._feature_names = feature_names

        self._model.fit(
            matrix,
            targets,
        )

        self._is_fitted = True

    def predict(
        self,
        features: list[dict[str, float]],
    ) -> list[float]:
        """Predict race times for the supplied features."""

        if not self._is_fitted:
            raise RuntimeError(
                "Model must be fitted before prediction"
            )

        matrix = [
            [
                sample[name]
                for name in self._feature_names
            ]
            for sample in features
        ]

        predictions = self._model.predict(matrix)

        return [
            float(prediction)
            for prediction in predictions
        ]

    @property
    def feature_names(self) -> list[str]:
        """Return the feature names used during training."""

        if not self._is_fitted:
            return []

        return list(self._feature_names)

    @property
    def feature_importances(self) -> dict[str, float]:
        """Return the learned importance of each feature."""

        if not self._is_fitted:
            return {}

        return {
            name: float(importance)
            for name, importance in zip(
                self._feature_names,
                self._model.feature_importances_,
            )
        }