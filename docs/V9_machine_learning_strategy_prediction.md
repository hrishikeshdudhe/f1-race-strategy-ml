# V9 — Machine Learning Strategy Prediction

## 1. Overview

Version 9 introduces the first machine learning layer to the F1 race strategy simulation project.

Up to V8, the project focused on deterministic race simulation, strategy generation, optimization, race-condition modeling, and generation of datasets containing simulated strategy results.

V9 builds on that simulation framework by treating the generated strategy results as a supervised machine learning dataset.

The main objective of V9 is:

> Use characteristics of a race strategy to predict its simulated total race time.

The version introduces a complete baseline machine learning workflow:

1. Generate simulated race strategies.
2. Convert strategies into numerical features.
3. Convert simulation results into an ML dataset.
4. Split the dataset into training and test sets.
5. Train a linear regression model.
6. Train a simple mean baseline model.
7. Compare the machine learning model against the baseline.
8. Calculate regression metrics.
9. Inspect model feature coefficients.
10. Analyze individual prediction errors.
11. Summarize prediction errors.
12. Validate the complete ML workflow with automated tests.

The implementation uses `scikit-learn` for the machine learning algorithms while keeping the project's simulation logic independent from the ML layer.

---

# 2. Starting Point from V8

V8 introduced the strategy dataset and extended the simulation framework with race-condition-aware strategy generation and evaluation.

The existing simulation framework could generate many different race strategies and evaluate their simulated race times.

The dataset generation process produces `StrategyResult` objects containing:

- the race strategy
- the simulated total race time

Conceptually:

    Race Strategy
         |
         v
      Simulation
         |
         v
    StrategyResult
         |
         +---- Strategy
         |
         +---- Total race time

V9 uses these existing simulation results as the source of training data.

No external F1 telemetry dataset is required at this stage.

This is intentional.

The first ML version is based entirely on the project's own deterministic simulation environment.

---

# 3. V9 Architecture

The ML functionality was separated into its own package:

    src/
    └── f1_strategy/
        ├── simulation/
        │   └── ...
        │
        └── ml/
            ├── __init__.py
            ├── baseline.py
            ├── dataset.py
            ├── experiment.py
            ├── features.py
            ├── metrics.py
            ├── model.py
            ├── pipeline.py
            ├── prediction.py
            └── prediction_summary.py

The ML workflow is:

    Simulation Dataset
           |
           v
    StrategyResult objects
           |
           v
    StrategyFeatureExtractor
           |
           v
    Numerical feature dictionaries
           |
           v
    StrategyMLDataset
           |
           v
    Train / Test Split
           |
           +-------------------+
           |                   |
           v                   v
    Mean Baseline       Linear Regression
           |                   |
           +---------+---------+
                     |
                     v
              Regression Metrics
                     |
                     v
           Prediction Error Analysis

---

# 4. Why Add Machine Learning?

The project originally determines strategy performance through direct simulation.

For example, a strategy can be simulated and its total race time calculated.

This is accurate within the simulation model, but it requires running the simulation.

Machine learning introduces another possibility:

    Strategy characteristics
              |
              v
           ML model
              |
              v
      Predicted race time

This makes it possible to investigate whether the relationship between strategy characteristics and race performance can be learned from previously simulated strategies.

This also establishes the foundation for future versions where more sophisticated models can be trained.

---

# 5. Machine Learning Dataset

## 5.1 StrategyMLDataset

A new `StrategyMLDataset` class was introduced to represent simulation results in an ML-friendly form.

The class accepts a list of `StrategyResult` objects.

Its responsibilities are:

- store the simulation results
- extract features from each strategy
- provide target values
- provide the number of samples
- expose feature names

The main interface is:

    dataset = StrategyMLDataset(results)

    dataset.features()
    dataset.targets()
    dataset.feature_names()
    len(dataset)

---

# 6. ML Targets

The prediction target is the actual simulated race time.

For each `StrategyResult`, the following value is used:

    result.total_time_seconds

This is converted into a floating-point value.

Therefore:

    Target = simulated total race time in seconds

For example:

    Strategy A -> 4527.77 s
    Strategy B -> 4565.08 s
    Strategy C -> 4532.18 s

These values become the supervised learning targets.

---

# 7. Feature Engineering

Machine learning models require numerical input.

A race strategy contains structured objects such as:

- stints
- tires
- pit stops
- lap counts

These objects therefore need to be converted into numerical features.

This is handled by:

    StrategyFeatureExtractor

located in:

    src/f1_strategy/ml/features.py

---

# 8. Strategy Features

The feature set contains strategy-level characteristics.

## 8.1 Number of Stints

    number_of_stints

Represents the total number of stints in the strategy.

Example:

    Soft -> Medium

contains:

    number_of_stints = 2

---

## 8.2 Number of Pit Stops

    number_of_pit_stops

Represents the number of pit stops in the strategy.

For example:

    Stint 1
       |
    Pit Stop
       |
    Stint 2

has:

    number_of_pit_stops = 1

---

## 8.3 Total Laps

    total_laps

Represents the total number of laps covered by all stints.

The value is obtained from:

    strategy.total_laps()

---

## 8.4 Pit Stop Time

    pit_stop_time_seconds

Represents the total time spent in pit stops.

It is calculated by summing the time contribution of all pit stops.

---

# 9. Tire Compound Features

The strategy's tire compounds are represented using counts.

The features are:

    soft_stints
    medium_stints
    hard_stints

For example:

    Soft -> Medium -> Hard

produces:

    soft_stints   = 1
    medium_stints = 1
    hard_stints   = 1

This converts categorical tire information into numerical features.

---

# 10. Stint Length Features

V9 also introduced statistics describing how the total race distance is distributed among stints.

The features are:

    average_stint_laps
    shortest_stint_laps
    longest_stint_laps
    stint_lap_range

---

## 10.1 Average Stint Length

    average_stint_laps

represents the mean number of laps per stint.

For:

    20 laps
    25 laps

the average is:

    22.5 laps

---

## 10.2 Shortest Stint

    shortest_stint_laps

represents the smallest stint length.

For:

    20, 25, 30

the value is:

    20

---

## 10.3 Longest Stint

    longest_stint_laps

represents the largest stint length.

For:

    20, 25, 30

the value is:

    30

---

## 10.4 Stint Lap Range

    stint_lap_range

is calculated as:

    longest stint - shortest stint

For:

    20, 25, 30

the range is:

    30 - 20 = 10

If all stints have the same length, the range becomes:

    0

This feature provides a simple measure of how evenly the race distance is distributed among stints.

---

# 11. Individual Stint Features

V9 also includes individual stint-length features.

For each stint:

    stint_1_laps
    stint_2_laps
    stint_3_laps
    ...

are generated dynamically.

For example:

    Strategy:

    Stint 1 = 20 laps
    Stint 2 = 30 laps

produces:

    stint_1_laps = 20
    stint_2_laps = 30

This allows the regression model to distinguish strategies based on how laps are allocated between individual stints.

---

# 12. Feature Extraction Implementation

The `StrategyFeatureExtractor` first collects all stint lengths.

Conceptually:

    stint_laps = [
        float(stint.number_of_laps)
        for stint in strategy.stints
    ]

It then initializes the main strategy-level features.

Tire compound counts are calculated by iterating over the stints.

The individual stint features are then generated using an index:

    for index, stint in enumerate(
        strategy.stints,
        start=1,
    ):
        features[f"stint_{index}_laps"] = ...

Finally, if at least one stint exists, the following statistics are calculated:

    average_stint_laps
    shortest_stint_laps
    longest_stint_laps
    stint_lap_range

The implementation also handles empty stint lists safely by leaving these statistical features at zero.

---

# 13. StrategyMLDataset Implementation

`StrategyMLDataset` connects the simulation results to the feature extraction system.

Its constructor stores the results:

    self.results = list(results)

and creates:

    self.feature_extractor = StrategyFeatureExtractor()

The `features()` method extracts numerical features from every strategy.

Conceptually:

    return [
        self.feature_extractor.extract(
            result.strategy
        )
        for result in self.results
    ]

The `targets()` method returns the simulated race times:

    return [
        float(result.total_time_seconds)
        for result in self.results
    ]

The dataset therefore provides a clean separation between:

    Simulation Results
           |
           v
    ML Dataset Representation
           |
           +---- Features
           |
           +---- Targets

---

# 14. Regression Model

V9 introduces:

    StrategyRegressionModel

located in:

    src/f1_strategy/ml/model.py

The model uses:

    sklearn.linear_model.LinearRegression

The purpose of the class is to wrap the scikit-learn implementation in a project-specific interface.

This keeps the rest of the project independent from the exact scikit-learn API.

---

# 15. Model Training

The model provides:

    fit(
        features,
        targets
    )

Before fitting, several validations are performed.

An empty feature dataset is rejected.

A mismatch between the number of feature samples and target values is rejected.

An empty feature dictionary is also rejected.

The feature names from the first sample are stored so that the same feature ordering can be used during prediction.

The feature dictionaries are converted into a numerical matrix.

Conceptually:

    Feature dictionaries
            |
            v
    Numerical feature matrix
            |
            v
    LinearRegression.fit()
            |
            v
        Trained model

---

# 16. Model Prediction

The model provides:

    predict(features)

Prediction is only allowed after the model has been fitted.

If prediction is requested before training, a `RuntimeError` is raised.

The model converts feature dictionaries into the same numerical matrix structure used during training.

The scikit-learn predictions are then converted to Python floats.

---

# 17. Model Feature Names

The model exposes:

    feature_names

This property returns the feature names used during training.

Before fitting, it returns an empty list.

After fitting, it returns the stored feature names.

This provides transparency into which features the model expects.

---

# 18. Regression Metrics

V9 uses:

    RegressionMetrics

to evaluate predictions.

The metrics include:

    MAE
    RMSE
    R²

---

## 18.1 Mean Absolute Error

MAE measures the average absolute difference between predicted and actual race times.

A lower MAE is better.

For example:

    actual:     4550 s
    predicted:  4553 s

produces an absolute error of:

    3 s

---

## 18.2 Root Mean Squared Error

RMSE penalizes larger errors more strongly than MAE.

This makes it useful for detecting whether the model occasionally produces large prediction errors.

A lower RMSE is better.

---

## 18.3 R² Score

R² measures how much of the variation in the target values is explained by the model.

The mean baseline establishes a useful reference point.

An R² close to zero means the model provides little improvement over simply predicting the mean.

A positive R² indicates that the model explains some of the variation in the target.

---

# 19. Mean Baseline

Before evaluating the linear regression model, V9 introduced a simple baseline:

    MeanBaselineRegressor

The baseline predicts the mean of the training target values for every test sample.

For example, if the training targets have a mean of:

    4535 s

then the baseline predicts:

    4535 s

for every test strategy.

This is intentionally simple.

The purpose is not to produce a strong model, but to establish a reference against which the machine learning model can be evaluated.

A machine learning model should demonstrate that it performs better than this simple baseline.

---

# 20. ML Pipeline

The different ML components are connected through:

    StrategyMLPipeline

located in:

    src/f1_strategy/ml/pipeline.py

The pipeline manages:

1. dataset preparation
2. feature extraction
3. target extraction
4. train/test splitting
5. model training
6. prediction
7. evaluation
8. prediction error generation

---

# 21. Dataset Preparation

The pipeline provides:

    prepare_dataset(results)

This converts a list of `StrategyResult` objects into:

    StrategyMLDataset

An empty result list is rejected.

This provides a clear boundary between the simulation layer and the ML layer.

---

# 22. Train/Test Split

The pipeline uses:

    sklearn.model_selection.train_test_split

The default configuration is:

    test_size = 0.2
    random_state = 42

Therefore, 80% of the data is used for training and 20% is held out for testing.

The random state ensures reproducibility.

For the current experiment:

    Total samples:       441
    Training samples:    352
    Test samples:         89

The pipeline stores the resulting training and test data so that it can later be evaluated.

---

# 23. Pipeline Training

Training follows this process:

    StrategyResult objects
            |
            v
    StrategyMLDataset
            |
            v
        Features
            |
            v
        Targets
            |
            v
      Train/Test Split
            |
            v
    StrategyRegressionModel
            |
            v
        Trained Model

The pipeline also prevents training on fewer than two samples because a train/test split requires enough data to create both subsets.

---

# 24. Pipeline Prediction

The pipeline provides:

    predict(results)

It requires the pipeline to have been trained first.

The supplied results are converted into an ML dataset.

Their features are passed to the trained regression model.

The result is a list of predicted race times.

---

# 25. Pipeline Evaluation

The pipeline provides:

    evaluate()

Evaluation is performed using the held-out test set.

The trained model predicts the test features.

Those predictions are compared with the stored test targets.

A `RegressionMetrics` object is returned.

This ensures that evaluation is always performed on data that was not used to train the model.

---

# 26. Prediction Error Representation

V9 introduced a `PredictionError` object.

It represents the relationship between:

- actual race time
- predicted race time
- signed prediction error
- absolute prediction error

Conceptually:

    PredictionError
        |
        +---- actual
        |
        +---- predicted
        |
        +---- error
        |
        +---- absolute_error

The signed error indicates whether the model over- or under-predicted.

The absolute error indicates the magnitude of the mistake regardless of direction.

---

# 27. Prediction Error Analysis

The ML pipeline provides:

    prediction_errors()

This generates a `PredictionError` object for every held-out test sample.

For each test sample:

    actual
    predicted
    error
    absolute_error

can therefore be inspected.

This is more informative than looking only at aggregate metrics.

For example:

    actual = 4564.080 s
    predicted = 4548.789 s
    error = -15.291 s

indicates that the model underestimated the actual race time by 15.291 seconds.

---

# 28. Prediction Error Summary

V9 introduced:

    PredictionErrorSummary

located in:

    src/f1_strategy/ml/prediction_summary.py

This class aggregates a collection of `PredictionError` objects.

It calculates:

    mean_signed_error
    mean_absolute_error
    maximum_absolute_error
    minimum_absolute_error

It also provides:

    largest_errors(count)

which returns the predictions with the largest absolute errors.

---

# 29. Mean Signed Error

The mean signed error measures overall prediction bias.

Positive values indicate that the model tends to predict higher values than the actual values.

Negative values indicate that the model tends to predict lower values than the actual values.

For the current experiment:

    Mean signed error: -0.261 s

This indicates very little overall systematic bias.

---

# 30. Mean Absolute Error from Error Analysis

The prediction error summary also calculates the mean absolute error directly from the individual prediction errors.

For the current experiment:

    Mean absolute error: 3.215 s

This agrees with the MAE reported by `RegressionMetrics`.

This provides an additional consistency check between the aggregate metrics and the individual prediction errors.

---

# 31. Largest Prediction Errors

The error summary can sort predictions according to their absolute error.

For the current experiment, the five largest errors were:

    1. actual=4564.080 s, predicted=4548.789 s, error=-15.291 s
    2. actual=4561.290 s, predicted=4548.031 s, error=-13.259 s
    3. actual=4561.290 s, predicted=4548.225 s, error=-13.065 s
    4. actual=4558.130 s, predicted=4546.751 s, error=-11.379 s
    5. actual=4565.080 s, predicted=4554.194 s, error=-10.886 s

These examples show that the model can produce considerably larger errors for some strategies even though its average error is relatively small.

---

# 32. Experiment Script

The complete ML experiment is implemented in:

    src/f1_strategy/ml/experiment.py

It can be executed using:

    python -m f1_strategy.ml.experiment

The experiment performs the complete workflow automatically.

It:

1. Generates the simulation dataset.
2. Trains the ML pipeline.
3. Evaluates the linear regression model.
4. Trains the mean baseline.
5. Evaluates the baseline.
6. Prints model metrics.
7. Prints feature coefficients.
8. Prints the regression intercept.
9. Generates prediction errors.
10. Calculates prediction error statistics.
11. Displays the largest prediction errors.

---

# 33. Experiment Dataset

The experiment uses:

    number_of_laps = 50
    base_lap_time = 90.0

The generated dataset contains:

    Samples: 441
    Training samples: 352
    Test samples: 89

The same random state is used for the train/test split:

    random_state = 42

This makes the experiment reproducible.

---

# 34. Baseline Results

The mean baseline produced:

    MAE: 10.107 s
    RMSE: 11.857 s
    R²: -0.0045

The negative R² indicates that the mean baseline does not explain the variation in race times and performs slightly worse than the idealized zero-error reference used in the R² calculation.

The important role of the baseline is to provide a simple benchmark for the regression model.

---

# 35. Linear Regression Results

The linear regression model produced:

    MAE: 3.215 s
    RMSE: 4.508 s
    R²: 0.8548

Compared with the mean baseline:

    Metric     Mean Baseline     Linear Regression
    ------------------------------------------------
    MAE        10.107 s          3.215 s
    RMSE       11.857 s          4.508 s
    R²         -0.0045           0.8548

The regression model therefore provides a substantial improvement over the simple mean baseline for this simulated dataset.

---

# 36. Interpretation of the Results

The model's MAE of:

    3.215 seconds

means that, on average, the predicted race time differs from the simulated race time by about 3.2 seconds.

The RMSE of:

    4.508 seconds

is higher than the MAE because larger errors receive greater weight in the RMSE calculation.

The R² score of:

    0.8548

indicates that the model captures a large portion of the variation in the simulated race times within this experiment.

However, this result should not be interpreted as equivalent to real-world F1 prediction performance.

The model is currently learning from the project's own simulation model.

It is therefore primarily demonstrating the machine learning workflow and the relationship between the engineered strategy features and the simulator's outputs.

---

# 37. Feature Coefficients

The linear regression model exposes its feature coefficients.

The experiment currently reports:

    hard_stints: 3.294797
    soft_stints: -1.908198
    medium_stints: -1.386599
    stint_lap_range: 0.427973
    shortest_stint_laps: -0.213987
    longest_stint_laps: 0.213987
    stint_2_laps: -0.002104
    stint_1_laps: 0.002104
    total_laps: -0.000000
    pit_stop_time_seconds: 0.000000
    number_of_pit_stops: 0.000000
    average_stint_laps: -0.000000
    number_of_stints: 0.000000

The model intercept is:

    4521.892513

The coefficients should not automatically be interpreted as direct physical F1 relationships.

They describe the relationships learned from the current simulated dataset and the particular feature representation used in V9.

---

# 38. Important Observation About Feature Coefficients

Several coefficients are effectively zero.

For example:

    total_laps: -0.000000
    pit_stop_time_seconds: 0.000000
    number_of_pit_stops: 0.000000
    number_of_stints: 0.000000

This does not necessarily mean those concepts are physically irrelevant.

The reason is that some features are structurally related to each other in the generated dataset.

For example:

- total laps may be constant
- the number of stints may determine the number of pit stops
- stint lengths may already encode total race distance
- some features may be correlated

Linear regression can therefore distribute explanatory power among correlated features.

This is an important observation for future feature engineering.

---

# 39. Prediction Error Results

The current experiment reports:

    Mean signed error: -0.261 s
    Mean absolute error: 3.215 s
    Maximum absolute error: 15.291 s
    Minimum absolute error: 0.002 s

The mean signed error is close to zero.

This means that although individual predictions can be too high or too low, there is little overall directional bias.

The minimum absolute error of:

    0.002 s

shows that at least one strategy was predicted almost exactly.

The maximum absolute error of:

    15.291 s

shows that the model still has difficult cases.

---

# 40. Testing Strategy

V9 significantly expanded the automated test suite.

Testing covers:

- ML dataset creation
- feature extraction
- regression metrics
- baseline regression
- regression model
- ML pipeline
- prediction errors
- prediction error summaries

The existing simulation tests from V1-V8 were also retained.

This was important because adding the ML layer should not break the existing simulation functionality.

---

# 41. ML Dataset Tests

Tests were added for `StrategyMLDataset`.

They verify:

- results are stored correctly
- features are generated
- targets are generated
- feature names are exposed
- dataset length is correct

---

# 42. ML Feature Tests

Tests were added for `StrategyFeatureExtractor`.

They verify:

- number of stints
- number of pit stops
- total laps
- pit stop time
- soft stint count
- medium stint count
- hard stint count
- individual stint lengths
- average stint length
- shortest stint
- longest stint
- stint lap range
- equal-length stint behavior

The equal-length case verifies that:

    stint_lap_range = 0

when all stints have the same number of laps.

---

# 43. ML Model Tests

Tests were added for `StrategyRegressionModel`.

They verify:

- successful model training
- prediction after training
- feature names
- invalid training data
- mismatched feature and target lengths
- empty feature dictionaries
- prediction before training

This protects the model wrapper from invalid states.

---

# 44. ML Pipeline Tests

Tests were added for `StrategyMLPipeline`.

They verify:

- invalid test sizes are rejected
- empty training data is rejected
- single-sample training is rejected
- datasets can be prepared
- training works
- train/test splitting is reproducible
- prediction works after training
- prediction before training is rejected
- evaluation returns `RegressionMetrics`
- metrics are valid
- evaluation before training is rejected
- prediction errors are returned
- prediction errors correspond to the test targets
- prediction error analysis requires training

---

# 45. Prediction Error Tests

Tests were added specifically for the prediction error representation.

They verify:

- actual values are stored
- predicted values are stored
- signed error is calculated correctly
- absolute error is calculated correctly
- prediction errors can be generated from the pipeline

This provides a reliable foundation for more advanced error analysis later.

---

# 46. Prediction Error Summary Tests

Tests were added for `PredictionErrorSummary`.

They verify:

- empty summaries return zero values
- mean signed error is calculated correctly
- mean absolute error is calculated correctly
- maximum absolute error is calculated correctly
- minimum absolute error is calculated correctly
- largest errors are sorted correctly
- requesting more errors than available works
- requesting zero errors returns an empty list
- negative counts are rejected

---

# 47. Test Suite Result

After completing the V9 implementation, the full project test suite contains:

    273 tests

The final test run produced:

    273 passed in 1.64s

No tests failed.

This confirms that the V9 functionality integrates successfully with the existing V1-V8 codebase.

---

# 48. Final V9 ML Workflow

The complete workflow implemented in V9 is:

    Simulation
        |
        v
    StrategyResult
        |
        v
    StrategyMLDataset
        |
        v
    StrategyFeatureExtractor
        |
        v
    Numerical Features
        |
        v
    Train/Test Split
        |
        +------------------------+
        |                        |
        v                        v
    Mean Baseline        Linear Regression
        |                        |
        +------------+-----------+
                     |
                     v
              RegressionMetrics
                     |
                     v
             PredictionError
                     |
                     v
          PredictionErrorSummary
                     |
                     v
              Experiment Report

---

# 49. Files Added or Modified in V9

The main ML files introduced or developed in V9 are:

    src/f1_strategy/ml/__init__.py
    src/f1_strategy/ml/baseline.py
    src/f1_strategy/ml/dataset.py
    src/f1_strategy/ml/experiment.py
    src/f1_strategy/ml/features.py
    src/f1_strategy/ml/metrics.py
    src/f1_strategy/ml/model.py
    src/f1_strategy/ml/pipeline.py
    src/f1_strategy/ml/prediction.py
    src/f1_strategy/ml/prediction_summary.py

Corresponding tests include:

    tests/test_ml_baseline.py
    tests/test_ml_dataset.py
    tests/test_ml_features.py
    tests/test_ml_metrics.py
    tests/test_ml_model.py
    tests/test_ml_pipeline.py
    tests/test_ml_prediction.py
    tests/test_ml_prediction_summary.py

The existing simulation and test files from previous versions remain part of the project.

---

# 50. Dependency

V9 introduced the use of `scikit-learn`.

The dependency is required for:

    LinearRegression

and:

    train_test_split

The package is installed inside the project's Python virtual environment.

The project continues to use Python 3.10.

---

# 51. Reproducibility

The ML experiment uses deterministic configuration where possible.

The train/test split uses:

    random_state = 42

This ensures that the same dataset and configuration produce the same train/test partition.

The deterministic simulation dataset also allows the experiment to be repeated consistently.

This is particularly useful when comparing future ML models against the V9 baseline.

---

# 52. What V9 Achieved

V9 transforms the project from a pure race strategy simulation into a simulation-plus-machine-learning system.

Before V9:

    Strategy
       |
       v
    Simulation
       |
       v
    Race Time

After V9:

    Strategy
       |
       v
    Simulation
       |
       +----------------------+
       |                      |
       v                      v
    Actual Time        Strategy Features
                              |
                              v
                         ML Model
                              |
                              v
                       Predicted Time
                              |
                              v
                       Error Analysis

This is the first version where the project learns from its own generated data.

---

# 53. Limitations of V9

The current implementation is intentionally a baseline ML system.

Important limitations include:

## 53.1 Synthetic Training Data

The model is trained using data generated by the project's simulator.

It is not trained on real-world F1 telemetry or race timing data.

Therefore, the model learns the simulator's behavior rather than real Formula 1 performance.

---

## 53.2 Linear Model

The current model is:

    LinearRegression

Real race strategy relationships can be nonlinear.

For example, tire degradation, fuel load, track temperature, traffic, weather, safety cars, and pit timing can interact in complex ways.

A linear model cannot capture all such interactions.

---

## 53.3 Limited Features

The current features mainly describe the structure of the strategy:

- stint counts
- tire compound counts
- stint lengths
- pit stop count
- pit stop time

More detailed physical and race-condition features could be added in future versions.

---

## 53.4 No Real-Time Prediction

V9 predicts the total simulated race time of a strategy.

It does not yet perform dynamic race-strategy prediction during an ongoing race.

---

## 53.5 No Model Persistence

The current version trains the model when the experiment runs.

A trained model is not yet saved and loaded from disk.

This can be addressed in a future version.

---

# 54. Lessons Learned in V9

Several important machine learning concepts were introduced through the implementation.

### 54.1 Feature Engineering

Machine learning quality depends heavily on how the original domain data is represented.

The project therefore converts structured race strategies into meaningful numerical features.

### 54.2 Baseline Models

A machine learning model should not be evaluated in isolation.

The mean baseline provides a simple reference point.

### 54.3 Train/Test Separation

The model must be evaluated on data that was not used for training.

This prevents misleading evaluation results.

### 54.4 Reproducibility

Using a fixed random state ensures repeatable train/test splits.

### 54.5 Error Analysis

Aggregate metrics such as MAE and RMSE are useful, but individual errors can reveal behavior that averages hide.

### 54.6 Automated Testing

Machine learning components are still software components and should therefore be tested like the rest of the application.

---

# 55. V9 Final Result

The final V9 experiment produced:

    Dataset
    -------
    Samples: 441
    Training samples: 352
    Test samples: 89

    Mean baseline
    -------------
    MAE: 10.107 s
    RMSE: 11.857 s
    R²: -0.0045

    Linear regression
    -----------------
    MAE: 3.215 s
    RMSE: 4.508 s
    R²: 0.8548

    Prediction error analysis
    -------------------------
    Mean signed error: -0.261 s
    Mean absolute error: 3.215 s
    Maximum absolute error: 15.291 s
    Minimum absolute error: 0.002 s

The complete test suite finished with:

    273 passed

Therefore, V9 successfully adds a complete baseline machine learning workflow without breaking the existing simulation system.

---

# 56. Conclusion

V9 is the transition from a simulation-focused F1 strategy project to a machine-learning-enabled system.

The project can now:

- generate strategy simulation data
- engineer numerical strategy features
- construct ML datasets
- train a regression model
- compare the model with a baseline
- evaluate model performance
- inspect learned feature coefficients
- analyze individual prediction errors
- summarize prediction quality
- run the entire workflow from the command line
- automatically test the ML functionality

The current model already demonstrates a substantial improvement over the mean baseline on the generated dataset.

More importantly, V9 establishes a clean and testable ML architecture that can be extended in future versions with improved features, more advanced models, model persistence, visualization, hyperparameter tuning, and eventually real-world or externally sourced F1 data.
