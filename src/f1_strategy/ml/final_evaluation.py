from dataclasses import dataclass

from f1_strategy.ml.cross_validation import (
    CrossValidationResult,
    ModelCrossValidator,
)
from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.model import StrategyRegressionModel
from f1_strategy.ml.random_forest import (
    StrategyRandomForestModel,
)


@dataclass(frozen=True)
class FinalModelEvaluation:
    """Final evaluation of one machine learning model."""

    model_name: str
    cross_validation: CrossValidationResult


class FinalModelEvaluator:
    """Evaluate the final set of machine learning models."""

    def __init__(
        self,
        number_of_folds: int = 5,
        random_state: int = 42,
    ):
        if number_of_folds < 2:
            raise ValueError(
                "number_of_folds must be at least 2"
            )

        self._number_of_folds = number_of_folds
        self._random_state = random_state

    def evaluate(
        self,
        features: list[dict[str, float]],
        targets: list[float],
    ) -> list[FinalModelEvaluation]:
        """Evaluate the final model configurations."""

        models = {
            "Linear Regression": (
                lambda: StrategyRegressionModel()
            ),
            "Random Forest": (
                lambda: StrategyRandomForestModel(
                    n_estimators=100,
                    random_state=42,
                )
            ),
            "Gradient Boosting": (
                lambda: StrategyGradientBoostingModel(
                    n_estimators=100,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=42,
                )
            ),
        }

        validator = ModelCrossValidator(
            models=models,
            number_of_folds=self._number_of_folds,
            random_state=self._random_state,
        )

        results = validator.evaluate(
            features=features,
            targets=targets,
        )

        return [
            FinalModelEvaluation(
                model_name=result.model_name,
                cross_validation=result,
            )
            for result in results
        ]