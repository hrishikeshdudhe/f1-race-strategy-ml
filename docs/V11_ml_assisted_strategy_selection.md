# V11 — ML-Assisted Race Strategy Selection

## Overview

V11 extends the machine learning functionality developed in V10 from passive race-time prediction to active race strategy selection.

Instead of only asking:

> How fast is this strategy?

the system can now ask:

> Given a set of candidate strategies, which strategy does the machine learning model predict will be fastest?

V11 also introduces race-condition-aware strategy selection, allowing the model to consider the conditions under which a strategy is evaluated.

The complete V11 workflow is:

```
Race strategies
      ↓
Race simulator
      ↓
Strategy evaluation dataset
      ↓
Machine learning model
      ↓
Candidate strategy predictions
      ↓
ML strategy selection
      ↓
Simulator validation
      ↓
Compare ML selection with simulator optimum
```

---

# 1. Objectives

The main objectives of V11 were:

1. Use the trained machine learning model to select race strategies.
2. Ensure that the ML model selects only from available candidate strategies.
3. Evaluate the selected strategy using the simulator.
4. Compare the ML-selected strategy with the simulator-optimal strategy.
5. Validate the selection process across multiple train/test splits.
6. Extend strategy selection to account for race conditions.
7. Maintain strict separation between training data and candidate strategies.

---

# 2. V11.1 — ML-Assisted Strategy Selection

## 2.1 Motivation

In V10, the machine learning models were evaluated primarily as regression models.

The model predicted race time for a strategy:

```
Strategy → Predicted race time
```

V11.1 changes this into a decision process:

```
Multiple candidate strategies
            ↓
      ML predictions
            ↓
Select lowest predicted race time
```

The simulator is then used to determine how good the ML decision actually was.

---

## 2.2 Data separation

The available strategies are divided into two groups:

```
All evaluated strategies
        │
        ├── Training strategies
        │
        └── Candidate strategies
```

The ML model is trained only on the training strategies.

The candidate strategies are not used during training.

This prevents the experiment from simply training and selecting on the same samples.

---

## 2.3 Strategy selector

The `MLStrategySelector` receives:

```
list[StrategyResult]
```

For each candidate strategy it:

1. Extracts strategy features.
2. Obtains an ML prediction.
3. Associates the prediction with the original strategy.
4. Sorts the strategies by predicted race time.
5. Selects the strategy with the lowest prediction.

The selector also returns the complete ranking of candidate strategies.

---

## 2.4 V11.1 result

Using the tuned Gradient Boosting model from V10:

```
Training strategies: 352
Candidate strategies: 89
```

The ML model selected:

```
SOFT (26 laps) → SOFT (24 laps)
```

with:

```
Predicted race time: 4519.075 s
Actual race time:    4518.080 s
```

The simulator identified:

```
SOFT (25 laps) → SOFT (25 laps)
```

as the fastest candidate:

```
Actual race time: 4518.000 s
```

Therefore:

```
Selection gap: 0.080 s
```

The ML model did not select the exact simulator optimum in this particular split, but the selected strategy was very close to the optimum.

---

# 3. V11.2 — Strategy Selection Validation

A single train/test split is not sufficient to determine whether the selection behaviour is stable.

V11.2 therefore repeats the complete strategy-selection process using five different random train/test splits.

The validation process is:

```
Generate strategies
        ↓
Evaluate strategies
        ↓
Split training/candidate data
        ↓
Train Gradient Boosting model
        ↓
Predict candidate strategies
        ↓
Select ML strategy
        ↓
Compare against simulator optimum
```

---

## 3.1 Validation metrics

The validation records:

* exact optimum selections
* exact optimum selection rate
* average selection gap
* minimum selection gap
* maximum selection gap

The selection gap is:

```
selected strategy time - fastest candidate time
```

A gap of zero means the ML system selected the simulator-optimal candidate.

---

## 3.2 V11.2 results

Five independent train/test splits were evaluated.

| Run | ML-selected strategy | Simulator optimum |     Gap |
| --- | -------------------- | ----------------- | ------: |
| 1   | SOFT 30 → SOFT 20    | SOFT 30 → SOFT 20 | 0.000 s |
| 2   | SOFT 26 → SOFT 24    | SOFT 25 → SOFT 25 | 0.080 s |
| 3   | SOFT 25 → SOFT 25    | SOFT 25 → SOFT 25 | 0.000 s |
| 4   | SOFT 25 → SOFT 25    | SOFT 25 → SOFT 25 | 0.000 s |
| 5   | SOFT 22 → SOFT 28    | SOFT 22 → SOFT 28 | 0.000 s |

Summary:

```
Validation runs:              5
Exact optimum selections:     4 / 5
Exact optimum selection rate: 80.0%
Average selection gap:        0.016 s
Minimum selection gap:        0.000 s
Maximum selection gap:        0.080 s
```

These results indicate that, within this synthetic simulation environment, the ML selector generally selected either the simulator optimum or a strategy with a very small performance gap.

---

# 4. V11.3 — Race-Condition-Aware Strategy Selection

V11.3 extends the ML feature representation beyond the strategy itself.

A strategy can perform differently depending on the race conditions under which it is evaluated.

The feature representation therefore becomes:

```
Strategy features
        +
Race-condition features
        ↓
Machine learning model
```

---

## 4.1 Race-condition features

The following race-condition features were added:

```
green_laps
yellow_laps
vsc_laps
safety_car_laps
race_condition_laps
race_condition_delay_seconds
```

The `RaceConditionFeatureExtractor` combines these features with the existing strategy features.

This allows the ML model to receive information about both:

```
What strategy is being used?
```

and:

```
Under what race conditions is it being evaluated?
```

---

## 4.2 Race-condition schedule

The V11.3 experiment uses a deterministic mixed-condition race.

The default condition is:

```
GREEN
```

Additional periods contain:

```
YELLOW
VSC
SAFETY CAR
```

For the 50-lap experiment the resulting schedule contains:

```
Green laps:       41
Yellow laps:       3
VSC laps:          3
Safety Car laps:   3
```

The simulated race-condition delay was:

```
162.000 s
```

All candidate strategies are evaluated against the same race-condition schedule.

This is important because the experiment is intended to compare strategies under identical race conditions rather than allowing each strategy to experience a different race.

---

# 5. V11.3 Results

The experiment used:

```
Training strategies: 352
Candidate strategies: 89
```

The ML system selected:

```
SOFT (25 laps) → SOFT (25 laps)
```

Prediction:

```
4680.843 s
```

Simulator result:

```
4679.704 s
```

The simulator identified the same strategy as the fastest candidate:

```
SOFT (25 laps) → SOFT (25 laps)
```

Therefore:

```
Selection gap: 0.000 s
```

The ML selector selected the simulator-optimal strategy for this race-condition scenario.

---

# 6. Architecture

The V11 ML architecture can be summarized as:

```
Race strategies
        │
        ▼
 Race simulator
        │
        ▼
  StrategyResult
        │
   ┌────┴────┐
   │         │
   ▼         ▼
Strategy   Race-condition
features   features
   │         │
   └────┬────┘
        │
        ▼
  Gradient Boosting
       model
        │
        ▼
  Predicted race times
        │
        ▼
   Strategy selector
        │
        ▼
  ML-selected strategy
        │
        ▼
   Race simulator
        │
        ▼
   Actual race time
        │
        ▼
   Compare with optimum
```

---

# 7. Implementation

The main V11 components are:

```
src/f1_strategy/ml/
├── strategy_selector.py
├── strategy_selection_experiment.py
├── strategy_selection_validation.py
├── race_condition_features.py
├── race_condition_strategy_selector.py
└── race_condition_strategy_selection_experiment.py
```

The corresponding tests include:

```
tests/
├── test_ml_strategy_selector.py
├── test_ml_strategy_selection_experiment.py
├── test_ml_strategy_selection_validation.py
├── test_race_condition_features.py
└── test_race_condition_strategy_selection.py
```

---

# 8. Testing

The complete project test suite passes:

```
351 passed
```

The tests cover:

* ML strategy selection
* prediction ranking
* invalid selector input
* strategy selection experiments
* multiple validation splits
* selection-gap calculations
* optimum-selection statistics
* race-condition feature extraction
* race-condition-aware strategy selection
* integration with the existing simulator

---

# 9. What V11 Demonstrates

V11 moves the project beyond simply building a regression model.

The system can now:

```
1. Generate candidate race strategies
2. Simulate their performance
3. Train a machine learning model
4. Predict unseen candidate strategies
5. Rank candidate strategies
6. Select a strategy automatically
7. Validate the decision against the simulator
8. Include race-condition information
```

This creates the foundation for an ML-assisted race strategy system rather than a standalone race-time prediction model.

---

# 10. Limitations

The results should not be interpreted as evidence that the system can predict or optimize real Formula 1 race strategies.

The current environment is a synthetic simulation.

Important limitations include:

* simplified tire degradation
* simplified pit-stop modelling
* simplified fuel modelling
* simplified race-condition modelling
* no real F1 telemetry
* no weather model
* no traffic model
* no driver-specific behaviour
* no tyre temperature model
* no overtaking model
* no detailed track-sector model
* no real-world race data
* limited strategy feature representation

The machine learning model is therefore learning relationships within the project's simulator rather than learning directly from real Formula 1 races.

---

# 11. Key Lessons

V11 introduced several important machine learning and software-engineering concepts.

### Train/test separation

The model must not be trained on the same candidate strategies that are used to evaluate its selection decisions.

### Regression versus decision-making

A regression model can predict race time, but a strategy-selection system must use those predictions to make a decision among competing candidates.

### Validation

A single experiment is not sufficient. Repeating the process across different data splits gives a better indication of whether the selection behaviour is stable.

### Feature engineering

Adding race-condition features allows the model to represent additional factors affecting race time.

### Simulator and ML integration

The simulator provides the environment and ground-truth evaluation, while machine learning provides an approximation that can be used to reduce the need for exhaustive evaluation.

---

# 12. V11 Conclusion

V11 successfully integrates machine learning into the race strategy simulation pipeline.

The project now contains a complete workflow from:

```
Strategy generation
        ↓
    Simulation
        ↓
 Dataset creation
        ↓
 Machine learning
        ↓
Strategy prediction
        ↓
Strategy selection
        ↓
Simulator validation
```

V11.3 additionally introduces race-condition-aware feature engineering and strategy selection.

The next stage is V12, which will integrate the project's simulation, machine learning and strategy-selection components into a final user-facing application and portfolio-ready implementation.
