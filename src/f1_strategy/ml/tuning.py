from dataclasses import dataclass
from typing import Callable

from f1_strategy.ml.cross_validation import (
    CrossValidationResult,
    ModelCrossValidator,
)


@dataclass(frozen=True)
class ModelConfiguration:
    """Configuration for one machine learning model."""

    name: str
    factory: Callable[[], object]


@dataclass(frozen=True)
class ModelTuningResult:
    """Cross-validation result for one model configuration."""

    configuration: ModelConfiguration
    evaluation: CrossValidationResult


class ModelTuner:
    """Compare multiple model configurations using cross-validation."""

    def __init__(
        self,
        configurations: list[ModelConfiguration],
        number_of_folds: int = 5,
        random_state: int = 42,
    ):
        if not configurations:
            raise ValueError(
                "At least one configuration is required"
            )

        self._configurations = list(
            configurations
        )

        self._number_of_folds = number_of_folds
        self._random_state = random_state

    def evaluate(
        self,
        features: list[dict[str, float]],
        targets: list[float],
    ) -> list[ModelTuningResult]:
        """Evaluate all model configurations."""

        results = []

        for configuration in self._configurations:
            validator = ModelCrossValidator(
                models={
                    configuration.name: (
                        configuration.factory
                    )
                },
                number_of_folds=self._number_of_folds,
                random_state=self._random_state,
            )

            evaluation = validator.evaluate(
                features=features,
                targets=targets,
            )[0]

            results.append(
                ModelTuningResult(
                    configuration=configuration,
                    evaluation=evaluation,
                )
            )

        return results