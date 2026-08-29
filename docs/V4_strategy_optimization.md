# V4 — Strategy Comparison and Optimization

## 1. Overview

Version 4 extends the F1 race simulator from evaluating a single predefined race strategy to comparing multiple strategies and identifying the fastest one.

In V3, the simulator introduced:

- Multiple tire stints
- Tire degradation
- Pit stops
- Race strategies
- Strategy validation

However, the user still had to decide which strategy to simulate.

V4 introduces an optimization layer that can evaluate several candidate strategies and determine which one produces the lowest total race time.

The central question of V4 is:

> Which of the available race strategies is fastest?

---

## 2. Evolution from V3

### V3

V3 evaluates one predefined strategy:

    Medium
        ↓
    Pit Stop
        ↓
    Hard
        ↓
    Total Race Time

The simulator answers:

> How fast is this strategy?

### V4

V4 evaluates multiple strategies:

    Strategy A
    Medium → Hard
        ↓
    Race Time

    Strategy B
    Soft → Hard
        ↓
    Race Time

    Strategy C
    Medium → Medium
        ↓
    Race Time

The optimizer then compares the results and selects the fastest strategy.

The simulator now answers:

> Which of these strategies is fastest?

---

## 3. Main Objective

The main objective of V4 is to introduce a basic optimization system on top of the existing race simulation.

The workflow is:

    Candidate Strategies
            ↓
    Simulate each strategy
            ↓
    Calculate total race time
            ↓
    Compare race times
            ↓
    Select fastest strategy

This is the first version of the project that makes an actual strategy decision rather than simply simulating a user-selected strategy.

---

## 4. New Component

V4 introduces:

    src/f1_strategy/simulation/optimizer.py

The new class is:

    StrategyOptimizer

Its responsibility is to compare multiple `RaceStrategy` objects.

The optimizer provides two main operations:

    evaluate()

and:

    find_fastest()

---

## 5. StrategyOptimizer

The optimizer is initialized with a baseline lap time.

Example:

    optimizer = StrategyOptimizer(90.0)

Here, `90.0` represents the baseline lap time in seconds.

The optimizer then receives one or more `RaceStrategy` objects.

Example:

    results = optimizer.evaluate(
        [strategy_a, strategy_b]
    )

The optimizer simulates each strategy independently and returns the corresponding race times.

---

## 6. Evaluating Multiple Strategies

The `evaluate()` method calculates the total race time for every supplied strategy.

For example:

    Strategy A → 558.74 seconds
    Strategy B → 557.33 seconds

The result contains both the original strategy object and its calculated time.

Conceptually:

    [
        (strategy_a, 558.74),
        (strategy_b, 557.33)
    ]

This allows the complete set of candidate strategies to be inspected rather than returning only the winner.

---

## 7. Finding the Fastest Strategy

The `find_fastest()` method uses the results of the evaluation and selects the strategy with the smallest total race time.

For example:

    Strategy A → 558.74 s
    Strategy B → 557.33 s

The optimizer returns:

    Strategy B
    557.33 seconds

The fastest strategy is therefore the strategy with the minimum simulated race time.

---

## 8. Optimization Concept

The V4 problem can be represented mathematically as:

    s* = argmin(time(s))

where:

- `s` represents a candidate strategy
- `time(s)` represents its simulated race time
- `s*` represents the fastest strategy

In simple terms:

> Evaluate all candidate strategies and choose the one with the lowest race time.

The current implementation performs an exhaustive comparison of the strategies supplied to it.

---

## 9. Exhaustive Search

V4 uses a simple exhaustive search approach.

If the optimizer receives:

    3 strategies

then all 3 strategies are evaluated.

If it receives:

    100 strategies

then all 100 strategies are evaluated.

The advantage is simplicity.

Every supplied candidate is evaluated, so the optimizer will always identify the fastest strategy among the supplied candidates.

The disadvantage is that the computational cost increases as the number of possible strategies increases.

This limitation becomes important as the project becomes more realistic.

---

## 10. Strategy Reusability

An important V4 design consideration is that evaluating a strategy should not permanently change the strategy's tire state.

In the current simulation model, a `Stint` ages its tire while it is being simulated.

Therefore, directly evaluating the same strategy multiple times could otherwise produce different results:

    First evaluation  → 558.74 s
    Second evaluation → 559.46 s

This would be undesirable for an optimizer.

To solve this, `StrategyOptimizer` creates a copy of the strategy before evaluating it.

The process is:

    Original Strategy
            ↓
    Copy Strategy
            ↓
    Copy Tires
            ↓
    Simulate Copy
            ↓
    Original Strategy remains unchanged

This means that a strategy can safely be evaluated multiple times.

For example:

    First evaluation  → 558.74 s
    Second evaluation → 558.74 s

The result is deterministic and repeatable.

---

## 11. Separation of Responsibilities

V4 introduces a clearer separation between simulation and optimization.

### RaceStrategy

Responsible for representing and simulating one race strategy.

It contains:

- Stints
- Tires
- Pit stops

Its main question is:

> How fast is this strategy?

### StrategyOptimizer

Responsible for comparing multiple strategies.

Its main question is:

> Which strategy is fastest?

This separation makes the project easier to extend in future versions.

---

## 12. Architecture

The overall architecture after V4 is:

    Track
      │
      └── Baseline lap time
                │
                ▼
              Race
                │
                ▼
          RaceStrategy
           │       │
           │       └── PitStop
           │
           └── Stint
                 │
                 └── Tire
                       │
                       └── TireCompound


    Multiple RaceStrategy objects
                │
                ▼
       StrategyOptimizer
          │          │
          │          └── find_fastest()
          │
          └── evaluate()
                │
                ▼
         Strategy comparison
                │
                ▼
          Fastest strategy

---

## 13. Example

Assume a race has a baseline lap time of:

    90 seconds

Two candidate strategies are supplied.

### Strategy A

    Medium → Hard

Simulated result:

    558.74 seconds

### Strategy B

    Soft → Hard

Simulated result:

    557.33 seconds

The optimizer compares:

    558.74 > 557.33

Therefore:

    Strategy B

is selected as the fastest strategy.

---

## 14. Automatic Decision Making

Before V4:

    User
      ↓
    Select strategy
      ↓
    Simulator
      ↓
    Race time

After V4:

    User
      ↓
    Provide candidate strategies
      ↓
    Optimizer
      ↓
    Simulate candidates
      ↓
    Compare race times
      ↓
    Select fastest strategy

This is an important conceptual step toward an automated race-strategy system.

---

## 15. Strategy Space

A race strategy can contain many decisions.

Examples include:

- Starting tire compound
- Tire compound after a pit stop
- Number of pit stops
- Stint lengths
- Pit-stop timing

For example:

    One-stop strategies

    Soft → Hard
    Medium → Hard
    Soft → Medium
    Medium → Soft

And:

    Two-stop strategies

    Soft → Medium → Hard
    Medium → Hard → Soft
    Soft → Hard → Medium

The current V4 optimizer does not generate these strategies automatically.

The candidate strategies are still created manually.

Automatic generation will be introduced in a later version.

---

## 16. Current Limitations

V4 is still a simplified simulation and optimization system.

### Manual strategy creation

The user must manually provide candidate strategies.

### Simplified tire model

Tire degradation is represented using a simple mathematical model.

### Constant baseline lap time

The baseline lap time does not currently change because of fuel load, weather, traffic, or other race conditions.

### No fuel model

Fuel consumption and fuel mass are not simulated.

### No weather

Rain, temperature, and changing track conditions are not included.

### No safety car

Safety-car periods are not modeled.

### No traffic

The interaction between cars is not simulated.

### No real race data

The system does not yet learn from historical F1 data.

---

## 17. Testing

V4 adds tests for the new optimizer.

The tests verify:

- Multiple strategies can be evaluated
- The correct number of results is returned
- Strategy race times are calculated correctly
- The fastest strategy is identified
- Empty strategy lists are rejected
- Repeated evaluation produces the same result

The complete test suite contains:

    31 tests

All 31 tests pass.

---

## 18. Test Suite Structure

The test suite now covers:

### Track

    test_track.py

Tests:

- Track creation
- Lap-time calculation
- Invalid track length
- Invalid lap count
- Invalid average speed

### Tire

    test_tire.py

Tests:

- Tire compounds
- Tire parameters
- Initial tire age
- Existing tire age
- Tire aging
- Negative age validation
- Tire performance
- Tire degradation

### Stint

    test_stint.py

Tests:

- Stint time calculation
- Tire aging
- Positive lap validation

### Pit Stop

    test_pit_stop.py

Tests:

- Pit-stop duration
- Positive duration validation
- Negative duration rejection

### Race

    test_race.py

Tests:

- Race time with multiple stints
- Independent tire aging
- Strategy coverage

### Strategy

    test_strategy.py

Tests:

- Strategy time calculation
- Stint/pit-stop consistency
- Single-stint strategies

### Optimizer

    test_optimizer.py

Tests:

- Strategy evaluation
- Fastest strategy selection
- Empty strategy validation
- Repeatable evaluation

---

## 19. Software Engineering Concepts Introduced

V4 demonstrates several important software-engineering concepts.

### Separation of concerns

Simulation and optimization are handled by separate classes.

### Reusable components

The optimizer can work with different `RaceStrategy` objects.

### Defensive validation

Invalid inputs are rejected using exceptions.

### Unit testing

Each component is tested independently.

### Deterministic behavior

The optimizer produces repeatable results for the same inputs.

### Abstraction

The optimizer hides the details of comparing strategies from the caller.

---

## 20. Python Concepts

V4 uses:

- Classes
- Objects
- Type hints
- Lists
- Tuples
- List iteration
- `min()`
- Lambda functions
- Exceptions
- Object copying
- Modular imports

A particularly useful Python construct is:

    min(
        results,
        key=lambda result: result[1]
    )

This selects the result with the smallest race time.

---

## 21. Version Progression

### V1 — Basic Race Simulator

    Track
      ↓
    Constant lap time
      ↓
    Race time

The first version established the basic simulation framework.

### V2 — Tire Degradation

    Track
      +
    Tire
      ↓
    Changing lap times

Tire performance became dependent on tire age.

### V3 — Pit Stops and Strategy

    Track
      +
    RaceStrategy
       │
       ├── Stint
       ├── PitStop
       └── Stint
      ↓
    Total race time

The project gained multi-stint strategies and pit stops.

### V4 — Strategy Optimization

    Multiple strategies
          ↓
    Simulate each
          ↓
    Compare race times
          ↓
    Select fastest strategy

The project now performs a basic automated strategy decision.

---

## 22. Why V4 Matters for the Final Project

The ultimate goal of the project is not simply to calculate race times.

The goal is to develop an F1 race-strategy prediction and simulation system.

V4 provides the first optimization layer needed for that goal.

The future system can follow this structure:

    Race Conditions
          ↓
    Simulation / Prediction
          ↓
    Candidate Strategies
          ↓
    Strategy Evaluation
          ↓
    Optimization
          ↓
    Recommended Strategy

This architecture can later incorporate machine learning.

---

## 23. Future Machine-Learning Connection

V4 itself is not machine learning.

It is a deterministic optimization system.

However, it creates an important foundation for ML.

Eventually, real race data can be introduced:

    Historical F1 Data
          │
          ├── Lap times
          ├── Tire degradation
          ├── Pit-stop times
          ├── Weather
          ├── Track characteristics
          └── Race conditions
                    ↓
             Machine Learning
                    ↓
           Predicted race behavior
                    ↓
            Strategy Optimizer
                    ↓
          Recommended Strategy

The optimizer could then use ML predictions instead of only simplified formulas.

---

## 24. Planned Future Versions

### V5 — Automatic Strategy Generation

Instead of manually creating strategies, the system will generate possible strategies automatically.

For example:

    Tire compounds
          +
    Stint lengths
          +
    Number of pit stops
          ↓
    Generate valid strategies
          ↓
    Evaluate strategies
          ↓
    Find fastest strategy

### V6 — More Realistic Race Simulation

Potential additions:

- Fuel consumption
- Fuel mass effect
- Weather
- Track temperature
- More realistic tire degradation
- Pit-lane time
- Safety-car periods

### V7 — Historical Data

Introduce real F1 race data and use it to calibrate the simulation.

### V8 — Machine Learning

Use historical data to predict:

- Lap times
- Tire degradation
- Pit-stop effects
- Race pace

The predictions can then be combined with the strategy optimizer.

---

## 25. Final V4 Status

Version:

    V4 — Strategy Comparison and Optimization

Status:

    Complete

Tests:

    31 passed

Main capabilities:

    ✓ Track simulation
    ✓ Tire compounds
    ✓ Tire degradation
    ✓ Multiple tire stints
    ✓ Pit stops
    ✓ Race strategies
    ✓ Strategy validation
    ✓ Multiple strategy evaluation
    ✓ Fastest strategy selection
    ✓ Repeatable strategy evaluation
    ✓ Automated unit testing
    ✓ Versioned documentation

The project has now progressed from a basic race-time calculator to a system capable of comparing different race strategies.

The next major step is:

    V5 — Automatic Strategy Generation

V5 will allow the simulator itself to generate candidate strategies rather than requiring them to be manually defined.