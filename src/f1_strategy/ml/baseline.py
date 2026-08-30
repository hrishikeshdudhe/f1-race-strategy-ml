class MeanBaselineRegressor:
    """Predict the mean value of the training targets."""

    def __init__(self):
        self._mean = None

    def fit(self, targets: list[float]) -> None:
        """Fit the baseline using the training targets."""

        if not targets:
            raise ValueError(
                "At least one target is required"
            )

        self._mean = sum(targets) / len(targets)

    def predict(self, count: int) -> list[float]:
        """Return the mean prediction for each sample."""

        if self._mean is None:
            raise RuntimeError(
                "Baseline must be fitted before prediction"
            )

        if count < 0:
            raise ValueError(
                "Prediction count cannot be negative"
            )

        return [
            float(self._mean)
            for _ in range(count)
        ]

    @property
    def mean(self) -> float | None:
        """Return the fitted mean target."""

        return self._mean