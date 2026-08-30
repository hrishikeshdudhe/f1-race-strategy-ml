from math import sqrt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


class RegressionMetrics:
    """Calculate regression performance metrics."""

    def __init__(
        self,
        actual: list[float],
        predicted: list[float],
    ):
        if not actual:
            raise ValueError(
                "At least one actual value is required"
            )

        if len(actual) != len(predicted):
            raise ValueError(
                "Actual and predicted values must "
                "have the same length"
            )

        self.actual = list(actual)
        self.predicted = list(predicted)

    @property
    def mae(self) -> float:
        """Return mean absolute error."""

        return float(
            mean_absolute_error(
                self.actual,
                self.predicted,
            )
        )

    @property
    def rmse(self) -> float:
        """Return root mean squared error."""

        mse = mean_squared_error(
            self.actual,
            self.predicted,
        )

        return float(sqrt(mse))

    @property
    def r2(self) -> float:
        """Return the coefficient of determination."""

        return float(
            r2_score(
                self.actual,
                self.predicted,
            )
        )

    def summary(self) -> str:
        """Return a human-readable metrics summary."""

        return (
            f"MAE: {self.mae:.3f} s\n"
            f"RMSE: {self.rmse:.3f} s\n"
            f"R²: {self.r2:.4f}"
        )