import pytest

from f1_strategy.ml.pipeline import StrategyMLPipeline
from f1_strategy.ml.metrics import RegressionMetrics
from f1_strategy.ml.prediction import PredictionError
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.strategy_result import StrategyResult
from f1_strategy.simulation.stint import Stint
from f1_strategy.simulation.tire import Tire, TireCompound


def make_result(
    total_time_seconds: float,
) -> StrategyResult:
    """Create a deterministic strategy result."""

    first_stint = Stint(
        tire=Tire(TireCompound.SOFT),
        number_of_laps=20,
    )

    second_stint = Stint(
        tire=Tire(TireCompound.MEDIUM),
        number_of_laps=25,
    )

    strategy = RaceStrategy(
        stints=[first_stint, second_stint],
        pit_stops=[PitStop(25.0)],
    )

    return StrategyResult(
        strategy=strategy,
        total_time_seconds=total_time_seconds,
    )


def make_results() -> list[StrategyResult]:
    """Create a small deterministic dataset."""

    return [
        make_result(500.0),
        make_result(510.0),
        make_result(520.0),
        make_result(530.0),
        make_result(540.0),
        make_result(550.0),
        make_result(560.0),
        make_result(570.0),
        make_result(580.0),
        make_result(590.0),
    ]


def test_pipeline_rejects_invalid_test_size():
    with pytest.raises(ValueError):
        StrategyMLPipeline(test_size=0.0)

    with pytest.raises(ValueError):
        StrategyMLPipeline(test_size=1.0)

    with pytest.raises(ValueError):
        StrategyMLPipeline(test_size=-0.1)

    with pytest.raises(ValueError):
        StrategyMLPipeline(test_size=1.1)


def test_pipeline_rejects_empty_training_data():
    pipeline = StrategyMLPipeline()

    with pytest.raises(ValueError):
        pipeline.train([])


def test_pipeline_rejects_single_training_sample():
    pipeline = StrategyMLPipeline()

    with pytest.raises(ValueError):
        pipeline.train(
            [make_result(500.0)]
        )


def test_pipeline_can_prepare_dataset():
    pipeline = StrategyMLPipeline()

    dataset = pipeline.prepare_dataset(
        make_results()
    )

    assert len(dataset) == 10


def test_pipeline_trains_successfully():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(
        make_results()
    )

    assert len(pipeline.train_features) == 8
    assert len(pipeline.train_targets) == 8
    assert len(pipeline.test_features) == 2
    assert len(pipeline.test_targets) == 2


def test_pipeline_test_split_is_reproducible():
    pipeline_a = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline_b = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    results = make_results()

    pipeline_a.train(results)
    pipeline_b.train(results)

    assert pipeline_a.train_targets == (
        pipeline_b.train_targets
    )

    assert pipeline_a.test_targets == (
        pipeline_b.test_targets
    )


def test_pipeline_predicts_after_training():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    results = make_results()

    pipeline.train(results)

    predictions = pipeline.predict(
        results[:2]
    )

    assert len(predictions) == 2

    for prediction in predictions:
        assert isinstance(
            prediction,
            float,
        )


def test_pipeline_requires_training_before_prediction():
    pipeline = StrategyMLPipeline()

    with pytest.raises(RuntimeError):
        pipeline.predict(
            [make_result(500.0)]
        )


def test_pipeline_evaluate_returns_regression_metrics():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(
        make_results()
    )

    metrics = pipeline.evaluate()

    assert isinstance(
        metrics,
        RegressionMetrics,
    )


def test_pipeline_evaluate_returns_valid_metrics():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(
        make_results()
    )

    metrics = pipeline.evaluate()

    assert metrics.mae >= 0.0
    assert metrics.rmse >= 0.0
    assert metrics.r2 <= 1.0


def test_pipeline_requires_training_before_evaluation():
    pipeline = StrategyMLPipeline()

    with pytest.raises(RuntimeError):
        pipeline.evaluate()


def test_pipeline_prediction_errors_return_prediction_error_objects():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(
        make_results()
    )

    errors = pipeline.prediction_errors()

    assert len(errors) == 2

    for error in errors:
        assert isinstance(
            error,
            PredictionError,
        )


def test_pipeline_prediction_errors_match_test_targets():
    pipeline = StrategyMLPipeline(
        test_size=0.2,
        random_state=42,
    )

    pipeline.train(
        make_results()
    )

    errors = pipeline.prediction_errors()

    actual_values = [
        error.actual
        for error in errors
    ]

    assert actual_values == (
        pipeline.test_targets
    )


def test_pipeline_requires_training_before_prediction_errors():
    pipeline = StrategyMLPipeline()

    with pytest.raises(RuntimeError):
        pipeline.prediction_errors()