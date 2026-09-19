from f1_strategy.ml.baseline import MeanBaselineRegressor
from f1_strategy.ml.comparison import ModelComparator
from f1_strategy.ml.final_evaluation import (
    FinalModelEvaluator,
)
from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.metrics import RegressionMetrics
from f1_strategy.ml.model import StrategyRegressionModel
from f1_strategy.ml.pipeline import StrategyMLPipeline
from f1_strategy.ml.prediction_summary import (
    PredictionErrorSummary,
)
from f1_strategy.ml.random_forest import (
    StrategyRandomForestModel,
)
from f1_strategy.ml.tuning import (
    ModelConfiguration,
    ModelTuner,
)
from f1_strategy.simulation.dataset import (
    StrategyDatasetGenerator,
)


def run_baseline_experiment() -> None:
    """Run the complete V10 machine learning evaluation."""

    dataset_generator = StrategyDatasetGenerator(
        number_of_laps=50,
        base_lap_time=90.0,
    )

    results = (
        dataset_generator
        .evaluate_strategies()
    )

    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(results)

    baseline = MeanBaselineRegressor()

    baseline.fit(
        pipeline.train_targets
    )

    baseline_predictions = baseline.predict(
        len(pipeline.test_targets)
    )

    baseline_metrics = RegressionMetrics(
        actual=pipeline.test_targets,
        predicted=baseline_predictions,
    )

    models = {
        "Linear Regression": pipeline.model,
        "Random Forest": StrategyRandomForestModel(
            n_estimators=100,
            random_state=42,
        ),
        "Gradient Boosting": StrategyGradientBoostingModel(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
        ),
    }

    comparator = ModelComparator(
        models
    )

    comparison_results = comparator.evaluate(
        train_features=pipeline.train_features,
        train_targets=pipeline.train_targets,
        test_features=pipeline.test_features,
        test_targets=pipeline.test_targets,
    )

    print("ML model comparison")
    print("===================")

    print(
        f"Samples: {len(results)}"
    )

    print(
        f"Training samples: "
        f"{len(pipeline.train_targets)}"
    )

    print(
        f"Test samples: "
        f"{len(pipeline.test_targets)}"
    )

    print()

    print("Mean baseline")
    print("-------------")

    print(
        baseline_metrics.summary()
    )

    print()

    for result in comparison_results:
        print(result.model_name)
        print("-" * len(result.model_name))
        print(result.metrics.summary())
        print()

    linear_model = pipeline.model

    print("Linear regression feature coefficients")
    print("--------------------------------------")

    sorted_coefficients = sorted(
        linear_model.coefficients.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    for feature_name, coefficient in (
        sorted_coefficients
    ):
        print(
            f"{feature_name}: "
            f"{coefficient:.6f}"
        )

    print()

    print(
        f"Intercept: "
        f"{linear_model.intercept:.6f}"
    )

    print()

    random_forest_model = models[
        "Random Forest"
    ]

    print("Random forest feature importances")
    print("---------------------------------")

    sorted_importances = sorted(
        random_forest_model.feature_importances.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for feature_name, importance in (
        sorted_importances
    ):
        print(
            f"{feature_name}: "
            f"{importance:.6f}"
        )

    print()

    gradient_boosting_model = models[
        "Gradient Boosting"
    ]

    print("Gradient boosting feature importances")
    print("-------------------------------------")

    sorted_importances = sorted(
        gradient_boosting_model.feature_importances.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for feature_name, importance in (
        sorted_importances
    ):
        print(
            f"{feature_name}: "
            f"{importance:.6f}"
        )

    print()

    errors = pipeline.prediction_errors()

    error_summary = PredictionErrorSummary(
        errors
    )

    print("Linear regression prediction error analysis")
    print("-------------------------------------------")

    print(
        f"Mean signed error: "
        f"{error_summary.mean_signed_error:.3f} s"
    )

    print(
        f"Mean absolute error: "
        f"{error_summary.mean_absolute_error:.3f} s"
    )

    print(
        f"Maximum absolute error: "
        f"{error_summary.maximum_absolute_error:.3f} s"
    )

    print(
        f"Minimum absolute error: "
        f"{error_summary.minimum_absolute_error:.3f} s"
    )

    print()

    print("Largest linear regression prediction errors")
    print("-------------------------------------------")

    for index, error in enumerate(
        error_summary.largest_errors(5),
        start=1,
    ):
        print(
            f"{index}. "
            f"actual={error.actual:.3f} s, "
            f"predicted={error.predicted:.3f} s, "
            f"error={error.error:+.3f} s"
        )

    print()

    dataset = pipeline.prepare_dataset(
        results
    )

    print("5-fold cross-validation")
    print("=======================")

    final_evaluator = FinalModelEvaluator(
        number_of_folds=5,
        random_state=42,
    )

    final_results = final_evaluator.evaluate(
        features=dataset.features(),
        targets=dataset.targets(),
    )

    for result in final_results:
        evaluation = result.cross_validation

        print()
        print(result.model_name)
        print("-" * len(result.model_name))

        print(
            f"Mean MAE: "
            f"{evaluation.mean_mae:.3f} s"
        )

        print(
            f"Std MAE: "
            f"{evaluation.std_mae:.3f} s"
        )

        print(
            f"Mean RMSE: "
            f"{evaluation.mean_rmse:.3f} s"
        )

        print(
            f"Std RMSE: "
            f"{evaluation.std_rmse:.3f} s"
        )

        print(
            f"Mean R²: "
            f"{evaluation.mean_r2:.4f}"
        )

        print(
            f"Std R²: "
            f"{evaluation.std_r2:.4f}"
        )

    tuning_configurations = [
        ModelConfiguration(
            name="Baseline",
            factory=lambda: StrategyGradientBoostingModel(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42,
            ),
        ),
        ModelConfiguration(
            name="More Trees",
            factory=lambda: StrategyGradientBoostingModel(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=3,
                random_state=42,
            ),
        ),
        ModelConfiguration(
            name="Lower Learning Rate",
            factory=lambda: StrategyGradientBoostingModel(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            ),
        ),
        ModelConfiguration(
            name="Deeper Trees",
            factory=lambda: StrategyGradientBoostingModel(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42,
            ),
        ),
        ModelConfiguration(
            name="Balanced",
            factory=lambda: StrategyGradientBoostingModel(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=3,
                random_state=42,
            ),
        ),
    ]

    tuner = ModelTuner(
        configurations=tuning_configurations,
        number_of_folds=5,
        random_state=42,
    )

    tuning_results = tuner.evaluate(
        features=dataset.features(),
        targets=dataset.targets(),
    )

    print()
    print("Gradient boosting hyperparameter comparison")
    print("============================================")

    for result in tuning_results:
        evaluation = result.evaluation

        print()
        print(
            result.configuration.name
        )
        print(
            "-" * len(
                result.configuration.name
            )
        )

        print(
            f"Mean MAE: "
            f"{evaluation.mean_mae:.3f} s"
        )

        print(
            f"Std MAE: "
            f"{evaluation.std_mae:.3f} s"
        )

        print(
            f"Mean RMSE: "
            f"{evaluation.mean_rmse:.3f} s"
        )

        print(
            f"Std RMSE: "
            f"{evaluation.std_rmse:.3f} s"
        )

        print(
            f"Mean R²: "
            f"{evaluation.mean_r2:.4f}"
        )

        print(
            f"Std R²: "
            f"{evaluation.std_r2:.4f}"
        )

    tuned_result = next(
        result
        for result in tuning_results
        if result.configuration.name
        == "Lower Learning Rate"
    )

    print()
    print("Final tuned configuration")
    print("==========================")

    print(
        "Model: Gradient Boosting"
    )

    print(
        "n_estimators: 100"
    )

    print(
        "learning_rate: 0.05"
    )

    print(
        "max_depth: 3"
    )

    print()

    print(
        f"Mean MAE: "
        f"{tuned_result.evaluation.mean_mae:.3f} s"
    )

    print(
        f"Mean RMSE: "
        f"{tuned_result.evaluation.mean_rmse:.3f} s"
    )

    print(
        f"Mean R²: "
        f"{tuned_result.evaluation.mean_r2:.4f}"
    )


if __name__ == "__main__":
    run_baseline_experiment()