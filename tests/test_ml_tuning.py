import pytest

from f1_strategy.ml.gradient_boosting import (
    StrategyGradientBoostingModel,
)
from f1_strategy.ml.tuning import (
    ModelConfiguration,
    ModelTuner,
)


def create_features(
    number_of_samples: int,
) -> list[dict[str, float]]:
    """Create deterministic feature data."""

    return [
        {
            "feature_a": float(index),
            "feature_b": float(index * 2),
        }
        for index in range(number_of_samples)
    ]


def create_targets(
    number_of_samples: int,
) -> list[float]:
    """Create deterministic target data."""

    return [
        float(index * 3 + 10)
        for index in range(number_of_samples)
    ]


def create_configuration(
    name: str,
) -> ModelConfiguration:
    """Create a deterministic test configuration."""

    return ModelConfiguration(
        name=name,
        factory=lambda: StrategyGradientBoostingModel(
            n_estimators=20,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
        ),
    )


def test_empty_configuration_list_is_rejected():
    with pytest.raises(
        ValueError,
        match="At least one configuration is required",
    ):
        ModelTuner([])


def test_single_configuration_is_evaluated():
    tuner = ModelTuner(
        configurations=[
            create_configuration(
                "Gradient Boosting"
            )
        ],
        number_of_folds=3,
        random_state=42,
    )

    results = tuner.evaluate(
        features=create_features(15),
        targets=create_targets(15),
    )

    assert len(results) == 1

    result = results[0]

    assert result.configuration.name == (
        "Gradient Boosting"
    )

    assert len(
        result.evaluation.folds
    ) == 3


def test_multiple_configurations_are_evaluated():
    configurations = [
        create_configuration(
            "Configuration A"
        ),
        create_configuration(
            "Configuration B"
        ),
    ]

    tuner = ModelTuner(
        configurations=configurations,
        number_of_folds=3,
        random_state=42,
    )

    results = tuner.evaluate(
        features=create_features(15),
        targets=create_targets(15),
    )

    assert len(results) == 2

    assert [
        result.configuration.name
        for result in results
    ] == [
        "Configuration A",
        "Configuration B",
    ]


def test_configuration_order_is_preserved():
    configurations = [
        create_configuration(
            "Second"
        ),
        create_configuration(
            "First"
        ),
    ]

    tuner = ModelTuner(
        configurations=configurations,
        number_of_folds=3,
        random_state=42,
    )

    results = tuner.evaluate(
        features=create_features(15),
        targets=create_targets(15),
    )

    assert [
        result.configuration.name
        for result in results
    ] == [
        "Second",
        "First",
    ]


def test_configuration_factory_creates_fresh_models():
    created_models = []

    def factory():
        model = StrategyGradientBoostingModel(
            n_estimators=20,
            random_state=42,
        )

        created_models.append(model)

        return model

    configuration = ModelConfiguration(
        name="Gradient Boosting",
        factory=factory,
    )

    tuner = ModelTuner(
        configurations=[configuration],
        number_of_folds=4,
        random_state=42,
    )

    tuner.evaluate(
        features=create_features(20),
        targets=create_targets(20),
    )

    assert len(created_models) == 4

    assert len(
        {
            id(model)
            for model in created_models
        }
    ) == 4


def test_same_configuration_is_reproducible():
    configuration = create_configuration(
        "Gradient Boosting"
    )

    tuner_a = ModelTuner(
        configurations=[configuration],
        number_of_folds=5,
        random_state=42,
    )

    tuner_b = ModelTuner(
        configurations=[configuration],
        number_of_folds=5,
        random_state=42,
    )

    features = create_features(20)
    targets = create_targets(20)

    results_a = tuner_a.evaluate(
        features,
        targets,
    )

    results_b = tuner_b.evaluate(
        features,
        targets,
    )

    evaluation_a = results_a[0].evaluation
    evaluation_b = results_b[0].evaluation

    assert evaluation_a.mean_mae == pytest.approx(
        evaluation_b.mean_mae
    )

    assert evaluation_a.mean_rmse == pytest.approx(
        evaluation_b.mean_rmse
    )

    assert evaluation_a.mean_r2 == pytest.approx(
        evaluation_b.mean_r2
    )