from sklearn.linear_model import LinearRegression


class StrategyRegressionModel:
    """Linear regression model for predicting race strategy time."""

    def __init__(self):
        self._model = LinearRegression()
        self._is_fitted = False

    def fit(
        self,
        features: list[dict[str, float]],
        targets: list[float],
    ) -> None:
        """Train the regression model."""

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
    def coefficients(self) -> dict[str, float]:
        """Return the learned coefficient for each feature."""

        if not self._is_fitted:
            return {}

        return {
            name: float(coefficient)
            for name, coefficient in zip(
                self._feature_names,
                self._model.coef_,
            )
        }

    @property
    def intercept(self) -> float | None:
        """Return the learned regression intercept."""

        if not self._is_fitted:
            return None

        return float(self._model.intercept_)