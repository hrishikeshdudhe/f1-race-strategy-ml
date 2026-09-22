# V12 – Final Integrated Application

## 1. Overview

V12 is the final base version of the F1 Race Strategy ML project.

The main objective of V12 was to transform the individual simulation and machine learning components developed in previous versions into a single, integrated application.

Earlier versions focused on developing individual capabilities:

- Race simulation
- Tire degradation
- Pit stops
- Strategy generation
- Strategy optimization
- Fuel modelling
- Race conditions
- Dataset generation
- Machine learning prediction
- Model comparison
- ML-assisted strategy selection

V12 combines these components into one reproducible workflow.

The final application can be configured from the command line, executes the complete simulation and machine learning pipeline, reports the selected strategy and its performance, and generates a visualization of the ML predictions.

V12 therefore represents the completion of the project's original base scope.

---

## 2. Objectives

The main objectives of V12 were:

1. Create a unified application entry point.
2. Separate application configuration from implementation logic.
3. Connect the simulation and machine learning components into one workflow.
4. Make important simulation and ML parameters configurable.
5. Provide a command-line interface.
6. Provide a visual comparison of predicted and simulated strategy performance.
7. Add integration tests for the complete application.
8. Ensure that the complete project remains reproducible.
9. Keep the architecture modular so that individual components can still be tested independently.
10. Finalize the project as a coherent Python software engineering and ML portfolio project.

---

## 3. Application Architecture

The V12 architecture introduces an application layer above the existing simulation and machine learning modules.

The overall workflow is:

```text
                    Command Line
                         |
                         v
              RaceStrategyApplication
                         |
              +----------+----------+
              |                     |
              v                     v
       Configuration           Race Conditions
              |                     |
              +----------+----------+
                         |
                         v
                Strategy Generator
                         |
                         v
                 Strategy Simulator
                         |
                         v
               Evaluated Strategies
                         |
                +--------+--------+
                |                 |
                v                 v
             Training          Candidates
             Strategies        Strategies
                |                 |
                v                 |
        Feature Extraction        |
                |                 |
                v                 |
          Gradient Boosting       |
              Training            |
                |                 |
                +--------+--------+
                         |
                         v
                  ML Predictions
                         |
                         v
                Strategy Selection
                         |
                         v
              Selected Strategy
                         |
                         v
              Simulator Comparison
                         |
                         v
                  Final Results
                         |
                         v
                  Visualization
```

This structure separates responsibilities between:

- configuration
- application orchestration
- simulation
- machine learning
- visualization
- command-line interaction

---

## 4. Application Layer

The application layer is located in:

```text
src/f1_strategy/application/
```

It contains:

```text
application/
├── __init__.py
├── cli.py
├── config.py
├── race_strategy_application.py
└── visualization.py
```

Each module has a specific responsibility.

---

## 5. Application Configuration

The configuration is implemented in:

```text
src/f1_strategy/application/config.py
```

The central configuration object is:

```python
RaceStrategyApplicationConfig
```

It contains the main parameters required by the integrated application.

The default configuration is:

```text
Number of laps:       50
Base lap time:        90.0 s
Test size:            0.20
Random state:         42
Estimators:           100
Learning rate:        0.05
Maximum tree depth:   3
Pit stop time:        20.0 s
```

Using a configuration object instead of hard-coded values provides several advantages:

- Reproducibility
- Easier experimentation
- Centralized parameter management
- Easier testing
- Separation between configuration and implementation

The configuration object is implemented as a frozen dataclass.

---

## 6. Configuration Validation

The application validates configuration values before execution.

Examples include:

```text
number_of_laps > 1
base_lap_time > 0
0 < test_size < 1
n_estimators > 0
learning_rate > 0
max_depth > 0
pit_stop_time_seconds >= 0
```

Invalid configuration values result in a `ValueError`.

This prevents invalid simulation or machine learning parameters from propagating into the application.

---

## 7. Race Condition Schedule

V12 uses a deterministic race-condition schedule.

The default 50-lap race contains:

```text
Green Flag       41 laps
Yellow Flag       3 laps
VSC               3 laps
Safety Car        3 laps
-----------------------
Total             50 laps
```

The schedule is generated automatically by the application.

The schedule uses the existing:

```text
RaceCondition
RaceConditionSchedule
```

components from the simulation layer.

The application does not directly calculate race-time effects. Instead, it creates the schedule and passes it to the simulation system.

This maintains separation between application orchestration and simulation logic.

---

## 8. Strategy Generation

The application creates a `StrategyGenerator` using the configured race parameters.

For the default 50-lap configuration, the generator produces:

```text
441 candidate strategies
```

These strategies represent possible two-stint tire strategies.

The application checks that strategy generation produced at least one valid strategy before continuing.

If no strategies are generated, execution stops with a `RuntimeError`.

---

## 9. Strategy Simulation

Every generated strategy is evaluated using the existing simulation framework.

The application creates a:

```python
StrategyOptimizer
```

with:

```text
base_lap_time
race_condition_schedule
```

The optimizer evaluates the generated strategies and returns detailed `StrategyResult` objects.

Each result contains the information required by the later ML pipeline, including the simulated total race time.

The important architectural principle is that the simulator remains independent from the ML model.

The simulator therefore provides the reference performance against which ML predictions can be evaluated.

---

## 10. Training and Candidate Strategies

After simulation, the evaluated strategies are divided into two groups:

```text
All evaluated strategies
          |
          +-------------------+
          |                   |
          v                   v
   Training strategies   Candidate strategies
```

The split uses `train_test_split()` with the configured:

- `test_size`
- `random_state`

For the default configuration:

```text
Total strategies:       441
Training strategies:    352
Candidate strategies:    89
```

The model is trained only using the training strategies.

The candidate strategies are held back for strategy selection.

This prevents the application from selecting a strategy using predictions generated from the same data on which the model was trained.

---

## 11. Feature Extraction

The V11 race-condition-aware feature extraction system is reused in V12.

The application creates:

```python
RaceConditionFeatureExtractor
```

and extracts numerical features from each training strategy.

The features encode characteristics of the strategy and its interaction with the race conditions.

The extracted feature representation is then passed to the machine learning model.

This keeps feature engineering separate from both simulation and model implementation.

---

## 12. Machine Learning Model

The integrated V12 application uses the gradient boosting model developed in V10 and V11.

The model is:

```python
StrategyGradientBoostingModel
```

with the default configuration:

```text
n_estimators = 100
learning_rate = 0.05
max_depth = 3
random_state = 42
```

The training target is:

```text
simulated total race time
```

Therefore, the model performs regression rather than classification.

Conceptually:

```text
Strategy features
       |
       v
Gradient Boosting
       |
       v
Predicted race time
```

Lower predicted race time represents a faster predicted strategy.

---

## 13. ML-Assisted Strategy Selection

After training, the model predicts the race time of every candidate strategy.

The predictions are passed to:

```python
RaceConditionMLStrategySelector
```

The selector ranks the candidate strategies according to their predicted race times.

The strategy with the lowest predicted time is selected by the ML system.

The application stores:

- Selected strategy
- Predicted time
- Ranked candidate strategies

The selected strategy is then compared against the actual simulated results.

---

## 14. Actual Fastest Candidate

In addition to the ML-selected strategy, the application determines the actual fastest candidate strategy using the simulator.

Conceptually:

```text
Candidate strategies
        |
        +--------------------+
        |                    |
        v                    v
    ML model             Simulator
        |                    |
        v                    v
ML-selected strategy   Actual fastest strategy
        |                    |
        +---------+----------+
                  |
                  v
             Comparison
```

The actual fastest candidate is found using the simulated `total_time_seconds`.

This provides a reference for measuring the quality of the ML-assisted selection.

---

## 15. Selection Gap

V12 calculates the difference between the simulated performance of the ML-selected strategy and the simulated performance of the actual fastest candidate.

The calculation is:

```text
Selection gap =
ML-selected actual time
-
Actual fastest candidate time
```

A gap of:

```text
0.000 s
```

means that the ML-selected strategy is also the fastest candidate according to the simulator.

A positive gap indicates that another candidate strategy had a lower simulated race time.

The metric is useful because it evaluates the ML system at the level that matters for strategy selection rather than only evaluating prediction error.

---

## 16. Race Condition Summary

The application exposes a summary of the race-condition schedule.

The result contains counts of laps for:

- Green
- Yellow
- VSC
- Safety Car

For the default 50-lap configuration:

```text
Green:       41 laps
Yellow:       3 laps
VSC:          3 laps
Safety Car:   3 laps
```

This summary is displayed by the CLI so that the user can understand the simulated race environment before interpreting the strategy result.

---

## 17. Application Result Object

The integrated workflow returns:

```python
RaceStrategyApplicationResult
```

instead of printing information directly from the application logic.

This result object contains:

- `training_strategies`
- `candidate_strategies`
- `selection`
- `actual_fastest_strategy`
- `race_condition_schedule`

It also provides calculated properties for:

- `selected_actual_time`
- `selected_predicted_time`
- `actual_fastest_time`
- `selection_gap`
- `race_condition_summary`

This design keeps the core application reusable.

For example, the CLI can consume the result and print it, while another future interface could consume the same result without changing the application logic.

---

## 18. Command-Line Interface

The CLI is implemented in:

```text
src/f1_strategy/application/cli.py
```

The Python package exposes the command:

```text
f1-strategy
```

The command is configured through `pyproject.toml`.

The default command is:

```bash
f1-strategy
```

The available parameters are:

```text
--laps
--base-lap-time
--pit-stop-time
--test-size
--random-state
```

For example:

```bash
f1-strategy --laps 30 --base-lap-time 92 --pit-stop-time 25
```

The CLI constructs the configuration object and passes it to the application.

This means that the CLI does not contain the simulation or ML implementation itself.

It acts as an interface to the application layer.

---

## 19. Example Default Execution

Running:

```bash
f1-strategy
```

produces output similar to:

```text
F1 Race Strategy ML
===================

Race configuration
------------------
Laps: 50
Base lap time: 90.0 s
Pit stop time: 20.0 s

Race conditions
---------------
Green: 41 laps
Yellow: 3 laps
VSC: 3 laps
Safety Car: 3 laps

Strategy search
---------------
Training strategies: 352
Candidate strategies: 89

ML-selected strategy
--------------------
Strategy: SOFT -> SOFT
Predicted race time: 4680.843 s
Actual race time: 4679.704 s

Actual fastest candidate
------------------------
Strategy: SOFT -> SOFT
Race time: 4679.704 s

Selection performance
---------------------
Gap to fastest candidate: 0.000 s

Visualization
-------------
Strategy prediction chart: strategy_predictions.png
```

The exact numerical values depend on the configured simulation parameters and random state.

---

## 20. Configurability

V12 removes important hard-coded application parameters.

One example is pit-stop duration.

Previously, the strategy generator directly created a pit stop using a fixed value of 20 seconds.

V12 changes this so that the generator accepts:

```text
pit_stop_time_seconds
```

The value is supplied by the application configuration.

This creates the following flow:

```text
CLI argument
     |
     v
ApplicationConfig
     |
     v
RaceStrategyApplication
     |
     v
StrategyGenerator
     |
     v
PitStop
```

This allows the same application to be executed with different pit-stop assumptions without modifying source code.

---

## 21. Visualization

The visualization system is implemented in:

```text
src/f1_strategy/application/visualization.py
```

The main function is:

```python
plot_strategy_predictions()
```

It plots the top ML-ranked candidate strategies and compares:

```text
ML prediction
vs.
Actual simulated race time
```

The x-axis represents the ML ranking of the strategies.

The y-axis represents race time in seconds.

The generated file is:

```text
strategy_predictions.png
```

The visualization is generated automatically by the CLI.

The output image is ignored by Git because it is a generated artifact.

---

## 22. Testing Strategy

V12 adds integration-level testing on top of the extensive unit tests developed in earlier versions.

The final test suite covers both individual components and the integrated workflow.

V12-specific tests cover:

- Default application execution
- Custom application configuration
- Configurable pit-stop duration
- Selected strategy timing
- Fastest strategy timing
- Selection-gap calculation
- Invalid configuration handling
- CLI execution with custom parameters
- CLI execution with default parameters

The final project test suite contains:

```text
361 passing tests
```

The tests were executed using:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest
```

The environment variable is used because of the project's local pytest plugin compatibility issue.

---

## 23. Integration Testing

The V12 integration tests verify that multiple components work together correctly.

The application tests execute the actual workflow rather than replacing the simulator or machine learning model with mocks.

The workflow is:

```text
Application
    ↓
Strategy generation
    ↓
Simulation
    ↓
Dataset split
    ↓
Feature extraction
    ↓
Model training
    ↓
ML prediction
    ↓
Strategy selection
    ↓
Simulator comparison
```

This verifies that the interfaces between the modules remain compatible.

---

## 24. Reproducibility

The application uses deterministic random-state configuration.

The default value is:

```text
random_state = 42
```

This is used for:

- Training/candidate dataset splitting
- Gradient boosting model initialization

Using a fixed random state makes the application behaviour reproducible under the same environment and configuration.

Users can change the value through:

```bash
f1-strategy --random-state <value>
```

This also makes it possible to experiment with different train/candidate splits.

---

## 25. Software Engineering Improvements

V12 is not primarily about introducing a new ML algorithm.

The main engineering improvement is the integration of the existing components into a coherent application.

### Separation of concerns

Simulation, ML, visualization and CLI responsibilities are separated.

### Centralized configuration

Important parameters are represented in one configuration object.

### Reusable application result

The application returns structured results instead of coupling the workflow directly to terminal output.

### Configurable simulation

Previously fixed assumptions such as pit-stop duration can now be changed through configuration.

### Integration testing

The final workflow is tested as a complete system.

### Command-line interface

The project can be executed as an installed Python command rather than requiring users to manually invoke internal modules.

---

## 26. Relationship to Previous Versions

V12 builds directly on the functionality developed in V1–V11.

```text
Simulation
    |
    +-- V1  Race simulation
    +-- V2  Tire degradation
    +-- V3  Pit stops
    +-- V4  Optimization
    +-- V5  Strategy generation
    +-- V6  Fuel modelling
    +-- V7  Race conditions
    |
    +-- V8  Dataset generation
    |
    +-- V9  ML prediction
    +-- V10 Model comparison and tuning
    +-- V11 ML-assisted strategy selection
    |
    +-- V12 Integrated application
```

V12 does not replace the previous architecture.

Instead, it provides an application layer that connects the existing systems.

---

## 27. Limitations

V12 remains a simplified simulation environment.

The project does not attempt to reproduce the full complexity of real Formula 1 strategy.

The simulation does not include detailed models for:

- Real telemetry
- Weather
- Traffic
- Overtaking
- Driver performance
- Team performance
- Track evolution
- Tire temperature
- Detailed vehicle dynamics
- Aerodynamic effects
- Real-time race control

The race conditions are simplified representations.

The machine learning dataset is generated by the simulator itself.

Therefore, the ML model learns relationships within the project's simulated environment.

The reported ML metrics and strategy-selection results should not be interpreted as evidence of real-world Formula 1 predictive performance.

---

## 28. Why V12 Is the Base Project Completion

The original project goal was to build a progressively more sophisticated F1 race-strategy system while learning simulation, optimization, machine learning and software engineering.

V12 completes that core progression.

The final system contains:

```text
Simulation
+
Strategy generation
+
Optimization
+
Race conditions
+
Dataset generation
+
Feature engineering
+
Machine learning
+
Model evaluation
+
ML-assisted selection
+
Application architecture
+
CLI
+
Visualization
+
Automated testing
```

This provides a complete Python-based portfolio project without requiring additional technologies merely for the sake of increasing complexity.

Future technologies such as PyTorch, Docker, FastAPI, databases or experiment tracking can be added later as independent extensions when there is a clear technical reason to use them.

---

## 29. Final V12 Workflow

The complete V12 workflow can be summarized as:

```text
User
 |
 | CLI configuration
 v
Application Configuration
 |
 v
Race Condition Schedule
 |
 v
Strategy Generator
 |
 v
441 Generated Strategies
 |
 v
Race Simulator
 |
 v
441 Evaluated Strategies
 |
 +-----------------------------+
 |                             |
 v                             v
352 Training                 89 Candidates
 |                             |
 v                             |
Feature Extraction             |
 |                             |
 v                             |
Gradient Boosting              |
 |                             |
 v                             |
ML Predictions <---------------+
 |
 v
Strategy Ranking
 |
 v
ML-Selected Strategy
 |
 v
Compare with Simulator
 |
 +-----------------------------+
 |                             |
 v                             v
Selected Actual Time       Fastest Candidate
 |                             |
 +-------------+---------------+
               |
               v
          Selection Gap
               |
               v
          Final CLI Output
               |
               v
       Strategy Visualization
```

---

## 30. Conclusion

V12 completes the base implementation of the F1 Race Strategy ML project.

The final system combines a modular race simulator with a machine learning pipeline and exposes the complete workflow through a configurable command-line application.

The resulting architecture provides a clear separation between:

- Simulation
- Machine learning
- Application orchestration
- Configuration
- Visualization
- User interaction

The project therefore demonstrates a progression from a simple simulation to an integrated Python application involving simulation, optimization, machine learning, testing and software architecture.

V12 is considered the final base version of the project. Further development should be treated as optional extensions rather than additional mandatory project versions.