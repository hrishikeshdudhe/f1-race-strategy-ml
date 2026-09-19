# F1 Race Strategy ML

A Python-based Formula 1 race strategy simulation and machine learning project.

The project started as a race strategy simulator and has evolved into a modular system for generating, evaluating, optimizing, and learning from F1-style race strategies.

The current version combines a race simulation framework with supervised machine learning models for predicting simulated race performance.

---

## Project Overview

Formula 1 race strategy involves balancing tire degradation, pit-stop costs, fuel consumption, race conditions, and stint lengths.

This project models these factors in a controlled simulation environment and uses the generated strategy data to investigate how machine learning can assist race strategy analysis.

The project is being developed incrementally through several versions:

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

- Race simulation framework
- Tire degradation modelling
- Multi-stint strategies
- Pit-stop modelling
- Strategy optimization
- Automatic strategy generation
- Fuel modelling
- Dynamic race conditions
- Strategy dataset generation
- Machine learning feature extraction
- Regression model training
- Model comparison
- Prediction error analysis
- Feature importance analysis
- 5-fold cross-validation
- Gradient Boosting hyperparameter tuning
- Final ML model evaluation

### Current version

**V10 — Machine Learning Model Comparison and Tuning**

### Next stage

**V11 — ML-assisted strategy selection and optimization**

---

## Technology Stack

- Python 3.10+
- NumPy
- scikit-learn
- pytest
- Git
- GitHub

The project currently focuses on Python and classical machine learning techniques.

More advanced machine learning and software engineering technologies will be introduced in later stages when they provide a clear benefit to the project.

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
│   └── ...
│
├── docs/
│   └── v10_machine_learning.md
│
├── pyproject.toml
└── README.md
```

---

# Simulation Framework

The simulation framework models a simplified F1 race environment.

A race strategy consists of one or more stints, with each stint specifying characteristics such as:

- tire compound
- stint length
- tire degradation
- pit-stop requirements
- fuel consumption
- race conditions

The simulator evaluates the resulting total race time.

The framework is deliberately simplified compared with a real Formula 1 race. Its purpose is to provide a controlled environment for experimenting with strategy algorithms and machine learning.

---

## Strategy Generation

The project can automatically generate valid race strategies under the simulation constraints.

Strategies can contain different numbers of stints and tire compound combinations.

Generated strategies are evaluated by the simulator, producing structured strategy results that can subsequently be used as machine learning data.

---

## Race Conditions

Race conditions can affect the performance of strategies during simulation.

The project includes infrastructure for modelling changing race conditions and applying condition schedules during a simulated race.

This provides a foundation for investigating strategy robustness under changing circumstances.

---

# Machine Learning

V9 introduced supervised machine learning to the project.

The objective is:

> Predict the simulated total race time of a race strategy from its strategy characteristics.

The ML pipeline operates on strategy results generated by the simulator.

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
       Model Evaluation
                 |
                 v
      Hyperparameter Tuning
```

---

## Dataset

The current V10 experiment generates:

- **441 strategy samples**
- **352 training samples**
- **89 test samples**
- **50 race laps**
- simulated total race time as the prediction target

The dataset is generated by the project's own simulator.

It is therefore **synthetic data**, not historical Formula 1 telemetry.

---

## Feature Engineering

The machine learning system extracts numerical features describing each strategy.

### Strategy features

- Number of stints
- Number of pit stops
- Total race laps
- Pit-stop time

### Tire compound features

- Number of soft-tire stints
- Number of medium-tire stints
- Number of hard-tire stints

### Stint distribution features

- Average stint length
- Shortest stint
- Longest stint
- Stint-length range

### Dynamic stint features

Individual stint lengths are also represented through features such as:

```text
stint_1_laps
stint_2_laps
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

Gradient Boosting currently provides the strongest cross-validation performance among the tested models.

---

# Model Evaluation

The project uses several evaluation approaches rather than relying on a single metric.

### Mean Absolute Error

MAE measures the average absolute difference between predicted and simulated race time.

Lower values indicate smaller prediction errors.

### Root Mean Squared Error

RMSE gives greater weight to larger prediction errors.

Lower values indicate better predictive accuracy.

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

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Mean baseline | 10.107 s | 11.857 s | -0.0045 |
| Linear Regression | 3.215 s | 4.508 s | 0.8548 |
| Random Forest | 2.054 s | 3.297 s | 0.9223 |
| Gradient Boosting | 1.571 s | 2.617 s | 0.9511 |

These results are based on the synthetic dataset generated by the simulator.

---

## 5-Fold Cross-Validation

The final model configurations produced:

| Model | Mean MAE | Mean RMSE | Mean R² |
|---|---:|---:|---:|
| Linear Regression | 3.227 s | 4.219 s | 0.8369 |
| Random Forest | 2.179 s | 3.456 s | 0.8894 |
| Gradient Boosting | 1.735 s | 2.635 s | 0.9353 |

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

| Configuration | Estimators | Learning rate | Max depth |
|---|---:|---:|---:|
| Baseline | 100 | 0.10 | 3 |
| More Trees | 200 | 0.10 | 3 |
| Lower Learning Rate | 100 | 0.05 | 3 |
| Deeper Trees | 100 | 0.10 | 4 |
| Balanced | 200 | 0.05 | 3 |

The configuration with the lowest mean MAE and RMSE and highest mean R² among those tested was:

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

| Feature | Importance |
|---|---:|
| shortest_stint_laps | 0.419665 |
| longest_stint_laps | 0.302202 |
| stint_lap_range | 0.118487 |
| hard_stints | 0.117884 |
| soft_stints | 0.030818 |
| medium_stints | 0.009736 |

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

This complements the aggregate MAE, RMSE, and R² metrics by showing the distribution and magnitude of individual prediction errors.

---

# Testing

The project uses `pytest` for automated testing.

The current test suite contains:

```text
327 tests passed
```

Tests cover:

- race simulation
- strategy generation
- optimization
- race conditions
- dataset generation
- feature extraction
- regression models
- baseline evaluation
- model comparison
- cross-validation
- Gradient Boosting
- Random Forest
- hyperparameter tuning
- final model evaluation

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

# Reproducibility

The ML experiments use fixed random states where applicable.

The main experiments use:

```text
random_state = 42
```

This allows model comparisons to be reproduced under the same project configuration.

---

# Limitations

This project is an engineering and machine learning experimentation platform rather than a real-world Formula 1 strategy predictor.

The current simulation does not fully model:

- real tire temperature behaviour
- detailed tire degradation curves
- weather
- traffic
- overtaking
- safety cars
- virtual safety cars
- red flags
- driver performance
- team performance
- track evolution
- aerodynamic effects
- real telemetry
- real-time race data

The machine learning dataset is also synthetic and generated from the project's own simulation assumptions.

Therefore, the reported ML metrics describe performance on this simulated environment and should not be interpreted as predictive performance for actual Formula 1 races.

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

Added systematic strategy dataset generation and race condition analysis.

## V9 — Machine Learning Strategy Prediction

Introduced supervised regression and feature engineering.

## V10 — Model Comparison and Tuning

Added:

- Linear Regression
- Random Forest
- Gradient Boosting
- model comparison
- 5-fold cross-validation
- feature importance analysis
- prediction error analysis
- hyperparameter tuning
- final model evaluation

## V11 — ML-Assisted Strategy Selection

Planned work:

- use the trained model to assist strategy selection
- evaluate candidate strategies
- combine simulation and ML predictions
- investigate ML-assisted optimization

## V12 — Final Integrated Application

Planned final stage:

- integrate the simulation and ML components
- provide a practical user-facing workflow
- improve visualization
- clean up the project architecture
- finalize documentation
- prepare the project as a complete portfolio application

---

# Future Development

After the core V12 system is complete, the project can be extended with more advanced engineering and machine learning technologies where they provide a genuine technical benefit.

Potential future directions include:

- PyTorch or TensorFlow
- deeper neural-network models
- advanced hyperparameter optimization
- experiment tracking
- model persistence
- REST APIs
- interactive dashboards
- Docker
- automated CI/CD
- databases
- cloud-based simulation
- larger-scale parallel simulation

These technologies are intentionally not introduced solely as additional tools. They will be considered when the project architecture provides a practical reason to use them.

---

# Version History

| Version | Description |
|---|---|
| V1 | Basic race simulation |
| V2 | Tire degradation |
| V3 | Pit stops and race strategy |
| V4 | Strategy optimization |
| V5 | Automatic strategy generation |
| V6 | Fuel and dynamic simulation |
| V7 | Race conditions |
| V8 | Strategy dataset and race condition analysis |
| V9 | Machine learning strategy prediction |
| V10 | Machine learning model comparison and tuning |
| V11 | ML-assisted strategy selection |
| V12 | Final integrated application |

---

# Author

**Hrishikesh Rajesh Dudhe**

M.Sc. Commercial Vehicle Technology

Germany

---

## License

This project is intended as a personal engineering and machine learning portfolio project.