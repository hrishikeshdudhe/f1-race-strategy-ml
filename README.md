# F1 Race Strategy ML

A Python-based Formula 1 race strategy simulation and machine learning project.

The project started as a race strategy simulator and has evolved into a modular system for generating, evaluating, optimizing, and learning from F1-style race strategies.

The current version combines a race simulation framework with supervised machine learning models for predicting simulated race performance and assisting strategy selection.

---

## Project Overview

Formula 1 race strategy involves balancing tire degradation, pit-stop costs, fuel consumption, race conditions, and stint lengths.

This project models these factors in a controlled simulation environment and uses the generated strategy data to investigate how machine learning can assist race strategy analysis and strategy selection.

The project is developed incrementally through several versions:

```text
V1  Basic race simulation
 |
V2  Tire degradation
 |
V3  Pit stops and race strategy
 |
V4  Strategy optimization
 |
V5  Automatic strategy generation
 |
V6  Fuel and dynamic race simulation
 |
V7  Race conditions
 |
V8  Strategy dataset and race condition analysis
 |
V9  Machine learning strategy prediction
 |
V10 Machine learning model comparison and tuning
 |
V11 ML-assisted strategy selection
 |
V12 Final integrated application
```

---

## Current Status

### Completed

* Race simulation framework
* Tire degradation modelling
* Multi-stint strategies
* Pit-stop modelling
* Strategy optimization
* Automatic strategy generation
* Fuel modelling
* Dynamic race conditions
* Strategy dataset generation
* Machine learning feature extraction
* Regression model training
* Model comparison
* Prediction error analysis
* Feature importance analysis
* 5-fold cross-validation
* Gradient Boosting hyperparameter tuning
* Final ML model evaluation
* ML-assisted strategy selection
* ML strategy-selection validation
* Race-condition-aware ML features
* Race-condition-aware strategy selection

### Current version

**V11 — ML-Assisted Strategy Selection**

### Next stage

**V12 — Final Integrated Application**

---

## Technology Stack

* Python 3.10+
* NumPy
* scikit-learn
* pytest
* Git
* GitHub

The project currently focuses on Python and classical machine learning techniques.

More advanced machine learning and software engineering technologies will be introduced in later stages when they provide a clear technical benefit to the project.

---

## Project Structure

```text
f1-race-strategy-ml/
|
├── src/
│   └── f1_strategy/
│       │
│       ├── ml/
│       │   ├── baseline.py
│       │   ├── comparison.py
│       │   ├── cross_validation.py
│       │   ├── dataset.py
│       │   ├── experiment.py
│       │   ├── features.py
│       │   ├── final_evaluation.py
│       │   ├── gradient_boosting.py
│       │   ├── metrics.py
│       │   ├── model.py
│       │   ├── pipeline.py
│       │   ├── prediction.py
│       │   ├── prediction_summary.py
│       │   ├── random_forest.py
│       │   ├── race_condition_features.py
│       │   ├── race_condition_strategy_selection_experiment.py
│       │   ├── race_condition_strategy_selector.py
│       │   ├── strategy_selection_experiment.py
│       │   ├── strategy_selection_validation.py
│       │   ├── strategy_selector.py
│       │   └── tuning.py
│       │
│       └── simulation/
│           ├── constraints.py
│           ├── dataset.py
│           ├── fuel.py
│           ├── generator.py
│           ├── optimizer.py
│           ├── pit_stop.py
│           ├── race.py
│           ├── race_condition.py
│           ├── race_condition_schedule.py
│           ├── run_strategy_search.py
│           ├── stint.py
│           ├── strategy.py
│           ├── strategy_result.py
│           ├── strategy_results.py
│           ├── tire.py
│           └── track.py
│
├── tests/
│   ├── test_ml_comparison.py
│   ├── test_ml_cross_validation.py
│   ├── test_ml_final_evaluation.py
│   ├── test_ml_gradient_boosting.py
│   ├── test_ml_random_forest.py
│   ├── test_ml_tuning.py
│   ├── test_ml_strategy_selection_validation.py
│   ├── test_race_condition_features.py
│   ├── test_race_condition_strategy_selection.py
│   └── ...
│
├── docs/
│   ├── V10_machine_learning_model_comparison_and_tuning.md
│   └── V11_ml_assisted_strategy_selection.md
│
├── pyproject.toml
└── README.md
```

---

# Simulation Framework

The simulation framework models a simplified F1 race environment.

A race strategy consists of one or more stints, with each stint specifying characteristics such as:

* tire compound
* stint length
* tire degradation
* pit-stop requirements
* fuel consumption
* race conditions

The simulator evaluates the resulting total race time.

The framework is deliberately simplified compared with a real Formula 1 race. Its purpose is to provide a controlled environment for experimenting with strategy algorithms and machine learning.

---

## Strategy Generation

The project can automatically generate valid race strategies under the simulation constraints.

Strategies can contain different numbers of stints and tire compound combinations.

Generated strategies are evaluated by the simulator, producing structured strategy results that can subsequently be used as machine learning data.

The strategy generator and optimizer are deliberately separated from the machine learning components so that ML models can be evaluated against simulator-generated ground truth.

---

## Strategy Optimization

The simulation framework provides systematic strategy evaluation and ranking.

Candidate strategies are evaluated using the simulator and ranked according to their simulated total race time.

This provides a simulator-based reference strategy that can be compared against strategies selected using machine learning.

The distinction between the simulator's actual evaluation and the ML model's prediction is important:

```text
Strategy
    |
    +----------------------+
    |                      |
    v                      v
Simulator             ML Model
    |                      |
    v                      v
Actual time           Predicted time
    |                      |
    +----------+-----------+
               |
               v
        Strategy comparison
```

---

## Race Conditions

Race conditions can affect the performance of strategies during simulation.

The project supports scheduled changes between:

* Green flag conditions
* Yellow flag conditions
* Virtual Safety Car (VSC)
* Safety Car

A `RaceConditionSchedule` assigns conditions to individual race laps.

The resulting condition-dependent lap times and delays are incorporated into the simulated race time.

This provides a foundation for investigating strategy selection under changing race circumstances.

---

# Machine Learning

V9 introduced supervised machine learning to the project.

The original objective was:

> Predict the simulated total race time of a race strategy from its strategy characteristics.

V11 extends this concept from prediction to **strategy selection**.

Instead of only predicting the performance of a strategy, the trained model can evaluate a set of previously unseen candidate strategies and rank them according to predicted race time.

The overall ML workflow is:

```text
Simulation
     |
     v
Generated Strategies
     |
     v
Strategy Results
     |
     v
Feature Extraction
     |
     v
Machine Learning Dataset
     |
     +-----------------------+
     |                       |
     v                       v
 Model Training       Cross Validation
     |                       |
     +-----------+-----------+
                 |
                 v
       Hyperparameter Tuning
                 |
                 v
          Trained Model
                 |
                 v
       Unseen Candidate Set
                 |
                 v
        ML Strategy Selection
                 |
                 v
       Compare with Simulator
```

---

## Dataset

The V10 experiment generates:

* **441 strategy samples**
* **352 training samples**
* **89 test samples**
* **50 race laps**
* simulated total race time as the prediction target

The dataset is generated by the project's own simulator.

It is therefore **synthetic data**, not historical Formula 1 telemetry.

The V11 strategy-selection experiments preserve the separation between training strategies and candidate strategies so that the model is not simply evaluated on the same candidates it used for training.

---

## Feature Engineering

The machine learning system extracts numerical features describing each strategy.

### Strategy features

* Number of stints
* Number of pit stops
* Total race laps
* Pit-stop time

### Tire compound features

* Number of soft-tire stints
* Number of medium-tire stints
* Number of hard-tire stints

### Stint distribution features

* Average stint length
* Shortest stint
* Longest stint
* Stint-length range

### Dynamic stint features

Individual stint lengths are also represented through features such as:

```text
stint_1_laps
stint_2_laps
stint_3_laps
...
```

---

# Machine Learning Models

V10 compares three regression approaches.

## Linear Regression

Used as an interpretable baseline model.

It provides coefficients that show the learned linear relationship between the strategy features and simulated race time.

## Random Forest

A tree-based ensemble model capable of modelling nonlinear relationships.

Feature importance values are also extracted for analysis.

## Gradient Boosting

A sequential tree-based ensemble model.

Gradient Boosting provided the strongest cross-validation performance among the tested models and became the model used for the V11 strategy-selection experiments.

---

# Model Evaluation

The project uses several evaluation approaches rather than relying on a single metric.

### Mean Absolute Error

MAE measures the average absolute difference between predicted and simulated race time.

Lower values indicate smaller prediction errors.

### Root Mean Squared Error

RMSE gives greater weight to larger prediction errors.

Lower values indicate smaller prediction errors.

### R²

R² measures how much of the variation in the target is explained by the model.

Higher values indicate greater explanatory performance.

### K-Fold Cross-Validation

The project uses 5-fold cross-validation to evaluate model performance across multiple train/validation splits.

Both mean performance and standard deviation are reported.

---

# V10 Results

## Initial Train/Test Comparison

The initial 80/20 evaluation produced:

| Model             |      MAE |     RMSE |      R² |
| ----------------- | -------: | -------: | ------: |
| Mean baseline     | 10.107 s | 11.857 s | -0.0045 |
| Linear Regression |  3.215 s |  4.508 s |  0.8548 |
| Random Forest     |  2.054 s |  3.297 s |  0.9223 |
| Gradient Boosting |  1.571 s |  2.617 s |  0.9511 |

These results are based on the synthetic dataset generated by the simulator.

---

## 5-Fold Cross-Validation

The final model configurations produced:

| Model             | Mean MAE | Mean RMSE | Mean R² |
| ----------------- | -------: | --------: | ------: |
| Linear Regression |  3.227 s |   4.219 s |  0.8369 |
| Random Forest     |  2.179 s |   3.456 s |  0.8894 |
| Gradient Boosting |  1.735 s |   2.635 s |  0.9353 |

The Gradient Boosting model also had:

```text
MAE standard deviation:  0.175 s
RMSE standard deviation: 0.170 s
R² standard deviation:   0.0143
```

---

# Hyperparameter Tuning

V10 performs a controlled comparison of Gradient Boosting configurations.

The tested configurations were:

| Configuration       | Estimators | Learning rate | Max depth |
| ------------------- | ---------: | ------------: | --------: |
| Baseline            |        100 |          0.10 |         3 |
| More Trees          |        200 |          0.10 |         3 |
| Lower Learning Rate |        100 |          0.05 |         3 |
| Deeper Trees        |        100 |          0.10 |         4 |
| Balanced            |        200 |          0.05 |         3 |

The configuration selected for the V11 experiments was:

```text
Gradient Boosting

n_estimators = 100
learning_rate = 0.05
max_depth = 3
random_state = 42
```

Its 5-fold cross-validation performance was:

```text
Mean MAE:  1.735 s
Mean RMSE: 2.635 s
Mean R²:   0.9353
```

Compared with the original configuration:

```text
MAE:  1.813 s -> 1.735 s

RMSE: 2.883 s -> 2.635 s

R²:   0.9224  -> 0.9353
```

The configuration is selected based on the tested configurations in this experiment. The project does not claim that these hyperparameters are globally optimal.

---

# Feature Importance

The Gradient Boosting model identified the following features as the most influential in the current simulation dataset:

| Feature             | Importance |
| ------------------- | ---------: |
| shortest_stint_laps |   0.419665 |
| longest_stint_laps  |   0.302202 |
| stint_lap_range     |   0.118487 |
| hard_stints         |   0.117884 |
| soft_stints         |   0.030818 |
| medium_stints       |   0.009736 |

The first four features account for approximately 95.8% of total feature importance.

These values describe relationships learned from the project's simulation data and should not be interpreted as real-world Formula 1 conclusions.

---

# Error Analysis

The project also analyses individual prediction errors.

For the initial Linear Regression model on the held-out test set:

```text
Mean signed error:      -0.261 s

Mean absolute error:     3.215 s

Maximum absolute error: 15.291 s

Minimum absolute error:  0.002 s
```

This complements the aggregate MAE, RMSE, and R² metrics by showing the magnitude of individual prediction errors.

---

# V11 — ML-Assisted Strategy Selection

V11 extends the project from **predicting strategy performance** to **using predictions to select strategies**.

The central idea is:

```text
Training strategies
       |
       v
Simulator
       |
       v
Training dataset
       |
       v
Gradient Boosting
       |
       v
TRAINED MODEL
       |
       v
New candidate strategies
       |
       v
ML predictions
       |
       v
ML-selected strategy
       |
       v
Simulator
       |
       v
Compare with actual fastest strategy
```

The important design constraint is that the model is trained on one subset of strategies and selects from a separate candidate subset.

This prevents the experiment from simply training and evaluating on the exact same strategies.

---

## V11.1 — ML Strategy Selection

The first V11 stage introduced an `MLStrategySelector`.

The selector:

1. Receives candidate `StrategyResult` objects.
2. Extracts their strategy features.
3. Uses the trained Gradient Boosting model to predict race time.
4. Ranks candidates by predicted race time.
5. Selects the candidate with the lowest predicted time.
6. Compares the selected strategy with the simulator's actual fastest candidate.

In the initial experiment:

```text
Training strategies: 352
Candidate strategies: 89
```

The ML-selected strategy was:

```text
SOFT (26 laps) -> SOFT (24 laps)
```

with:

```text
Predicted race time: 4519.075 s
Actual race time:    4518.080 s
```

The actual fastest candidate was:

```text
SOFT (25 laps) -> SOFT (25 laps)

Actual race time: 4518.000 s
```

The resulting selection gap was:

```text
0.080 s
```

This demonstrated the basic ML-assisted selection workflow while also showing that the lowest predicted strategy does not necessarily have to be the simulator's exact optimum.

---

# V11.2 — Strategy Selection Validation

The second V11 stage tested the ML strategy-selection process across five different train/candidate splits.

The validation used:

```text
Race length:       50 laps
Base lap time:     90 s
Test size:         20%
Random states:     1, 2, 3, 4, 5
Model:             Tuned Gradient Boosting
```

The results were:

```text
Validation runs: 5

Exact optimum selections: 4/5
Exact optimum selection rate: 80.0%

Average selection gap: 0.016 s
Minimum selection gap: 0.000 s
Maximum selection gap: 0.080 s
```

Individual runs produced:

```text
Run 1: gap = 0.000 s
Run 2: gap = 0.080 s
Run 3: gap = 0.000 s
Run 4: gap = 0.000 s
Run 5: gap = 0.000 s
```

These results describe performance within the project's synthetic simulation environment.

They should not be interpreted as an 80% strategy-selection accuracy for real Formula 1 races.

---

# V11.3 — Race-Condition-Aware Strategy Selection

The third V11 stage extends the ML feature space to include race-condition information.

The new `RaceConditionFeatureExtractor` combines:

### Strategy features

* Number of stints
* Number of pit stops
* Total laps
* Pit-stop time
* Tire compound counts
* Stint-length statistics
* Individual stint lengths

### Race-condition features

* Green laps
* Yellow laps
* VSC laps
* Safety Car laps
* Total race-condition laps
* Race-condition delay in seconds

The model therefore receives information about both the strategy itself and the race environment under which the strategy is evaluated.

---

## V11.3 Race Condition Scenario

The experiment uses a deterministic 50-lap race-condition schedule:

```text
Green laps:       41
Yellow laps:       3
VSC laps:          3
Safety Car laps:   3

Race-condition delay: 162.000 s
```

All candidate strategies are evaluated under the same race-condition schedule.

---

## V11.3 Results

The race-condition-aware ML selector selected:

```text
SOFT (25 laps) -> SOFT (25 laps)
```

with:

```text
Predicted race time: 4680.843 s
Actual race time:    4679.704 s
```

The simulator's actual fastest candidate was also:

```text
SOFT (25 laps) -> SOFT (25 laps)

Actual race time: 4679.704 s
```

The resulting selection gap was:

```text
0.000 s
```

The top ML predictions were:

```text
1. SOFT (25 laps) -> SOFT (25 laps)
2. SOFT (26 laps) -> SOFT (24 laps)
3. SOFT (23 laps) -> SOFT (27 laps)
4. SOFT (20 laps) -> SOFT (30 laps)
5. SOFT (31 laps) -> SOFT (19 laps)
6. SOFT (25 laps) -> MEDIUM (25 laps)
7. SOFT (24 laps) -> MEDIUM (26 laps)
8. SOFT (27 laps) -> MEDIUM (23 laps)
9. MEDIUM (26 laps) -> SOFT (24 laps)
10. MEDIUM (27 laps) -> SOFT (23 laps)
```

The result demonstrates the complete race-condition-aware selection workflow:

```text
Race condition schedule
          |
          v
Strategy simulation
          |
          v
StrategyResult
          |
          v
Race-condition feature extraction
          |
          v
Trained ML model
          |
          v
Candidate predictions
          |
          v
ML-selected strategy
          |
          v
Comparison with simulator optimum
```

As with the previous V11 experiments, these results are specific to the project's synthetic simulation environment.

---

# V11 Architecture

The current system separates simulation, optimization, machine learning, and strategy selection:

```text
                    SIMULATION
                        |
                        v
              Strategy Generator
                        |
                        v
               Race Simulator
                        |
                        v
                StrategyResult
                        |
              +---------+---------+
              |                   |
              v                   v
       Feature Extraction   Strategy Optimizer
              |                   |
              v                   v
       ML Training Data     Actual Performance
              |
              v
       Gradient Boosting
              |
              v
        Trained ML Model
              |
              v
       Unseen Candidates
              |
              v
       ML Strategy Selector
              |
              v
       Predicted Ranking
              |
              v
       Simulator Comparison
```

This separation allows the ML component to be evaluated against an independently calculated simulator result.

---

# Testing

The project uses `pytest` for automated testing.

The current test suite contains:

```text
351 tests passed
```

Tests cover:

* race simulation
* strategy generation
* optimization
* race conditions
* race-condition schedules
* dataset generation
* feature extraction
* race-condition feature extraction
* regression models
* baseline evaluation
* model comparison
* cross-validation
* Gradient Boosting
* Random Forest
* hyperparameter tuning
* final model evaluation
* ML strategy selection
* ML strategy-selection validation
* race-condition-aware strategy selection

Run the complete test suite with:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/hrishikeshdudhe/f1-race-strategy-ml.git

cd f1-race-strategy-ml
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the project:

```bash
pip install -e .
```

Install development dependencies if required:

```bash
pip install pytest scikit-learn numpy
```

---

# Running the ML Experiment

With the virtual environment activated:

```bash
python -m f1_strategy.ml.experiment
```

The experiment generates the strategy dataset and performs:

1. Model comparison
2. Feature analysis
3. Prediction error analysis
4. 5-fold cross-validation
5. Gradient Boosting hyperparameter comparison
6. Final tuned model evaluation

---

# Running V11 Strategy Selection

The V11 strategy-selection experiments are implemented as separate modules so that the prediction and selection workflows can be evaluated independently.

The project contains experiments for:

```text
ML strategy selection
        |
        +-- V11.1 basic ML-assisted selection
        |
        +-- V11.2 multi-split validation
        |
        +-- V11.3 race-condition-aware selection
```

The corresponding implementation is located in:

```text
src/f1_strategy/ml/

strategy_selector.py
strategy_selection_experiment.py
strategy_selection_validation.py
race_condition_features.py
race_condition_strategy_selector.py
race_condition_strategy_selection_experiment.py
```

---

# Reproducibility

The ML experiments use fixed random states where applicable.

The main experiments use:

```text
random_state = 42
```

The V11.2 validation additionally evaluates multiple fixed random states:

```text
1
2
3
4
5
```

This allows the experiments to be reproduced under the same project configuration.

---

# Limitations

This project is an engineering and machine learning experimentation platform rather than a real-world Formula 1 strategy predictor.

The current simulation is intentionally simplified and does not fully model:

* real tire temperature behaviour
* detailed real-world tire degradation curves
* weather
* traffic
* overtaking
* driver performance
* team performance
* track evolution
* aerodynamic effects
* real telemetry
* real-time race data
* detailed vehicle dynamics

Race conditions such as yellow flags, VSC, and Safety Car are modelled in a simplified form. They are represented through lap-time multipliers and scheduled race-condition delays rather than detailed race-control or vehicle-dynamics models.

The machine learning dataset is synthetic and generated from the project's own simulation assumptions.

Therefore, the reported ML metrics describe performance on this simulated environment and should not be interpreted as predictive performance for actual Formula 1 races.

The V11 selection experiments also compare ML-selected strategies against simulator-generated ground truth. This demonstrates the architecture and behaviour of the system but does not establish real-world Formula 1 strategy effectiveness.

---

# Development Roadmap

## V1 — Basic Race Simulator

Implemented the initial race simulation framework.

## V2 — Tire Degradation

Introduced tire degradation and compound-specific behaviour.

## V3 — Pit Stops and Race Strategy

Added multi-stint strategies and pit-stop modelling.

## V4 — Strategy Optimization

Added systematic strategy evaluation and optimization.

## V5 — Automatic Strategy Generation

Added automatic generation of valid race strategies.

## V6 — Fuel and Dynamic Simulation

Added fuel consumption and dynamic race simulation behaviour.

## V7 — Race Conditions

Introduced changing race conditions and condition schedules.

## V8 — Strategy Dataset

Added systematic strategy dataset generation and race-condition analysis.

## V9 — Machine Learning Strategy Prediction

Introduced supervised regression and feature engineering.

## V10 — Model Comparison and Tuning

Added:

* Linear Regression
* Random Forest
* Gradient Boosting
* model comparison
* 5-fold cross-validation
* feature importance analysis
* prediction error analysis
* hyperparameter tuning
* final model evaluation

## V11 — ML-Assisted Strategy Selection

Added:

* ML-based candidate strategy selection
* separation of training and candidate strategies
* strategy prediction ranking
* multi-split strategy-selection validation
* race-condition-aware feature extraction
* race-condition-aware strategy selection
* comparison against simulator ground truth

## V12 — Final Integrated Application

Planned final stage:

* integrate the simulation and ML components
* provide a practical user-facing workflow
* improve visualization
* clean up the project architecture
* finalize documentation
* prepare the project as a complete portfolio application

---

# Future Development

After the core V12 system is complete, the project can be extended with more advanced engineering and machine learning technologies where they provide a genuine technical benefit.

Potential future directions include:

* PyTorch or TensorFlow
* deeper neural-network models
* advanced hyperparameter optimization
* experiment tracking
* model persistence
* REST APIs
* interactive dashboards
* Docker
* automated CI/CD
* databases
* cloud-based simulation
* larger-scale parallel simulation

These technologies are intentionally not introduced solely as additional tools. They will be considered when the project architecture provides a practical reason to use them.

---

# Version History

| Version | Description                                  |
| ------- | -------------------------------------------- |
| V1      | Basic race simulation                        |
| V2      | Tire degradation                             |
| V3      | Pit stops and race strategy                  |
| V4      | Strategy optimization                        |
| V5      | Automatic strategy generation                |
| V6      | Fuel and dynamic simulation                  |
| V7      | Race conditions                              |
| V8      | Strategy dataset and race condition analysis |
| V9      | Machine learning strategy prediction         |
| V10     | Machine learning model comparison and tuning |
| V11     | ML-assisted strategy selection               |
| V12     | Final integrated application                 |

---

# Author

**Hrishikesh Rajesh Dudhe**

M.Sc. Commercial Vehicle Technology

Germany

---

## License

This project is intended as a personal engineering and machine learning portfolio project.
