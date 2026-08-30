from f1_strategy.ml.baseline import MeanBaselineRegressor
from f1_strategy.ml.metrics import RegressionMetrics
from f1_strategy.ml.pipeline import StrategyMLPipeline
from f1_strategy.ml.prediction_summary import (
    PredictionErrorSummary,
)
from f1_strategy.simulation.dataset import (
    StrategyDatasetGenerator,
)


def run_baseline_experiment() -> None:
    """Compare a mean baseline against linear regression."""

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

    regression_metrics = pipeline.evaluate()

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

    print("ML baseline comparison")
    print("======================")
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

    print("Linear regression")
    print("-----------------")
    print(
        regression_metrics.summary()
    )
    print()

    print("Feature coefficients")
    print("--------------------")

    coefficients = pipeline.model.coefficients

    sorted_coefficients = sorted(
        coefficients.items(),
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
        f"{pipeline.model.intercept:.6f}"
    )

    print()

    errors = pipeline.prediction_errors()

    error_summary = PredictionErrorSummary(
        errors
    )

    print("Prediction error analysis")
    print("-------------------------")
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

    print("Largest prediction errors")
    print("-------------------------")

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


if __name__ == "__main__":
    run_baseline_experiment()