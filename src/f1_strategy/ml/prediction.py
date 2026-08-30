from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionError:
    """Represent the prediction error for one sample."""

    actual: float
    predicted: float

    @property
    def error(self) -> float:
        """Return signed prediction error."""

        return self.predicted - self.actual

    @property
    def absolute_error(self) -> float:
        """Return absolute prediction error."""

        return abs(self.error)