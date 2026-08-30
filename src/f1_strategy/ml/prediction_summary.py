from f1_strategy.ml.prediction import PredictionError


class PredictionErrorSummary:
    """Summarize prediction errors from an ML evaluation."""

    def __init__(
        self,
        errors: list[PredictionError],
    ):
        self.errors = list(errors)

    @property
    def mean_signed_error(self) -> float:
        """Return the mean signed prediction error."""

        if not self.errors:
            return 0.0

        return sum(
            error.error
            for error in self.errors
        ) / len(self.errors)

    @property
    def mean_absolute_error(self) -> float:
        """Return the mean absolute prediction error."""

        if not self.errors:
            return 0.0

        return sum(
            error.absolute_error
            for error in self.errors
        ) / len(self.errors)

    @property
    def maximum_absolute_error(self) -> float:
        """Return the largest absolute prediction error."""

        if not self.errors:
            return 0.0

        return max(
            error.absolute_error
            for error in self.errors
        )

    @property
    def minimum_absolute_error(self) -> float:
        """Return the smallest absolute prediction error."""

        if not self.errors:
            return 0.0

        return min(
            error.absolute_error
            for error in self.errors
        )

    def largest_errors(
        self,
        count: int = 5,
    ) -> list[PredictionError]:
        """Return the predictions with the largest errors."""

        if count < 0:
            raise ValueError(
                "count must be non-negative"
            )

        return sorted(
            self.errors,
            key=lambda error: error.absolute_error,
            reverse=True,
        )[:count]