# V5 — Automatic Strategy Generation and Search

## 1. Overview

Version 5 extends the F1 race strategy simulator from manually defined strategy comparison to automatic strategy generation and search.

In V4, the optimizer could compare several strategies, but those strategies had to be created manually.

V5 removes this limitation.

The system can now:

1. Generate candidate strategies automatically
2. Vary tire-compound combinations
3. Vary stint lengths
4. Evaluate all generated strategies
5. Identify the fastest strategy
6. Execute the strategy search through a Python command-line interface

The project has therefore progressed from:

    Manually define strategies
            ↓
    Compare strategies

to:

    Define race parameters
            ↓
    Automatically generate strategies
            ↓
    Evaluate strategies
            ↓
    Select fastest strategy

---

## 2. Evolution from V4

### V4

The user manually creates strategies.

Example:

    Strategy A:
    Medium → Hard

    Strategy B:
    Soft → Hard

    Strategy C:
    Medium → Soft

    ↓

    StrategyOptimizer

    ↓

    Fastest strategy

The optimizer is automated, but the strategy candidates are not.

### V5

The strategy candidates are generated automatically.

    Race parameters
          ↓
    StrategyGenerator
          ↓
    Generate candidate strategies
          ↓
    StrategyOptimizer
          ↓
    Find fastest strategy

This is the first version where the complete strategy-search process is automated.

---

## 3. Main Objective

The main objective of V5 is to automatically explore a defined strategy space.

Instead of manually asking:

    "Should I use Soft → Hard?"

the program can consider:

    Soft → Soft
    Soft → Medium
    Soft → Hard
    Medium → Soft
    Medium → Medium
    Medium → Hard
    Hard → Soft
    Hard → Medium
    Hard → Hard

and different stint-length distributions.

For a 6-lap race, examples include:

    1 + 5
    2 + 4
    3 + 3
    4 + 2
    5 + 1

The system combines these decisions to create candidate strategies.

---

# 4. New Components

V5 introduces two important components.

### StrategyGenerator

File:

    src/f1_strategy/simulation/generator.py

Responsible for automatically creating candidate `RaceStrategy` objects.

### Strategy Search Runner

File:

    src/f1_strategy/simulation/run_strategy_search.py

Responsible for connecting strategy generation and optimization into a single high-level workflow.

The existing `StrategyOptimizer` from V4 is reused.

---

# 5. StrategyGenerator

The `StrategyGenerator` class receives the total number of race laps.

Example:

    generator = StrategyGenerator(6)

The generator then creates valid two-stint strategies for the race.

The basic structure is:

    StrategyGenerator
          │
          ├── Tire compound combinations
          │
          └── Stint-length combinations
                    ↓
              RaceStrategy objects

---

# 6. Tire-Compound Combinations

There are currently three tire compounds:

    SOFT
    MEDIUM
    HARD

For a two-stint strategy, every compound can be combined with every other compound.

This produces:

    3 × 3 = 9

compound combinations.

The combinations include:

    SOFT   → SOFT
    SOFT   → MEDIUM
    SOFT   → HARD

    MEDIUM → SOFT
    MEDIUM → MEDIUM
    MEDIUM → HARD

    HARD   → SOFT
    HARD   → MEDIUM
    HARD   → HARD

The generator creates these combinations automatically using Python's `itertools.product()`.

---

# 7. Stint-Length Generation

V5.2 introduces automatic generation of stint lengths.

For a race with six laps and exactly two stints, the total number of laps must always equal six.

Therefore, the possible splits are:

    1 + 5
    2 + 4
    3 + 3
    4 + 2
    5 + 1

Each split represents a possible pit-stop location.

For example:

    2 + 4

means:

    Stint 1 → 2 laps
    Pit stop
    Stint 2 → 4 laps

The generator ensures that:

    first_stint_laps + second_stint_laps
    = total_race_laps

---

# 8. Combining Compounds and Stint Lengths

The key V5 concept is that tire choices and stint lengths are combined.

For a 6-lap race:

    9 compound combinations

and:

    5 stint-length combinations

Therefore:

    9 × 5 = 45

candidate strategies.

For example:

    SOFT → HARD
    1 lap → 5 laps

or:

    SOFT → HARD
    3 laps → 3 laps

or:

    MEDIUM → SOFT
    4 laps → 2 laps

Each combination becomes a complete `RaceStrategy`.

---

# 9. Automatic Strategy Generation

The generation process is:

    Total race laps
            ↓
    Determine possible stint splits
            ↓
    Generate tire combinations
            ↓
    Combine tire choices with stint splits
            ↓
    Create RaceStrategy objects

For a 6-lap race:

    45 RaceStrategy objects

are generated.

The generator does not decide which strategy is best.

Its responsibility is only:

> Create the possible candidate strategies.

---

# 10. Strategy Validation

The generated strategies use the existing `RaceStrategy` validation.

A valid two-stint strategy must contain:

    2 stints
    1 pit stop

because:

    number of stints = number of pit stops + 1

The generator therefore creates:

    Stint
      ↓
    PitStop
      ↓
    Stint

for every candidate strategy.

It also ensures that:

    total stint laps = total race laps

This prevents the generator from producing incomplete race strategies.

---

# 11. Strategy Search

V5.3 connects the generator to the existing optimizer.

The high-level process is:

    StrategyGenerator
            ↓
    Generate candidate strategies
            ↓
    StrategyOptimizer
            ↓
    Evaluate every strategy
            ↓
    Find minimum race time
            ↓
    Return fastest strategy

The generator and optimizer therefore have separate responsibilities.

---

# 12. Separation of Responsibilities

### StrategyGenerator

Question:

> What strategies are possible?

Responsibilities:

- Generate tire combinations
- Generate stint-length combinations
- Create valid `RaceStrategy` objects

### StrategyOptimizer

Question:

> Which strategy is fastest?

Responsibilities:

- Evaluate strategies
- Calculate race times
- Compare results
- Select the fastest strategy

### Strategy Search Runner

Question:

> How do I run the complete search?

Responsibilities:

- Create the generator
- Generate strategies
- Create the optimizer
- Search for the fastest strategy
- Display the result

This separation makes the architecture easier to maintain and extend.

---

# 13. High-Level Search Function

V5 introduces:

    find_fastest_generated_strategy()

The function accepts:

    number_of_laps
    base_lap_time

For example:

    find_fastest_generated_strategy(
        number_of_laps=6,
        base_lap_time=90.0
    )

Internally it performs:

    Create StrategyGenerator
            ↓
    Generate strategies
            ↓
    Create StrategyOptimizer
            ↓
    Evaluate strategies
            ↓
    Return fastest strategy

This provides a simple interface for running the complete search.

---

# 14. Command-Line Interface

V5.4 adds a simple executable entry point.

The search can be started using:

    python -m f1_strategy.simulation.run_strategy_search

The program generates the candidate strategies and prints the fastest result.

Example output structure:

    Generated strategies: 45

    Fastest strategy:
      Stint 1: SOFT - 3 laps
      Stint 2: HARD - 3 laps

    Total race time: XX.XX seconds

The exact result depends on the tire-performance model.

---

# 15. Why a Command-Line Interface Matters

Previously, the project was mainly used through Python classes and unit tests.

The command-line runner gives the project a simple user-facing entry point.

The workflow becomes:

    Terminal
       ↓
    Run Python module
       ↓
    Generate strategies
       ↓
    Optimize
       ↓
    Display recommendation

This is an important step toward turning the project into a usable application.

---

# 16. Mathematical Representation

The V5 search can be viewed as a discrete optimization problem.

A strategy can be represented as:

    Strategy = {
        tire compounds,
        stint lengths,
        pit stops
    }

For two stints:

    Strategy =
        (compound_1, laps_1,
         compound_2, laps_2)

subject to:

    laps_1 + laps_2 = total_race_laps

and:

    laps_1 > 0
    laps_2 > 0

The optimizer then solves:

    s* = argmin(time(s))

over the generated set of valid strategies.

---

# 17. Exhaustive Search

V5 uses exhaustive search.

This means every generated candidate is evaluated.

For the 6-lap example:

    45 candidates

are simulated.

The optimizer then selects the candidate with the smallest race time.

The major advantage is simplicity and completeness within the defined strategy space.

If the strategy space contains 45 valid candidates, all 45 are considered.

---

# 18. Scalability

The number of possible strategies increases as the race becomes more complex.

For two stints:

    3 tire compounds ×
    (number_of_laps - 1) stint splits

For a 6-lap race:

    3² × 5 = 45

For a 50-lap race:

    3² × 49 = 441

For more stints, the number of possible combinations grows much faster.

For example, with three stints, we would need to consider:

    Tire combinations
            ×
    Three-way lap splits

This creates a combinatorial search problem.

This is one reason why future versions may need more sophisticated optimization methods.

---

# 19. Current Strategy Space

The current V5 implementation is deliberately limited to:

    2 stints
    1 pit stop

with:

    SOFT
    MEDIUM
    HARD

as available compounds.

The generator does not yet automatically generate:

- Three-stint strategies
- Four-stint strategies
- Multiple pit stops
- Minimum tire-age constraints
- Maximum stint lengths
- Mandatory compound rules
- Weather-dependent strategies
- Safety-car strategies

These will be considered in later versions.

---

# 20. Testing

V5 significantly expands the test suite.

The tests verify that:

- All tire combinations are generated
- All possible stint-length combinations are generated
- Generated strategies cover the complete race
- Generated strategies contain two stints
- Generated strategies use all tire compounds
- Invalid race lengths are rejected
- Generated strategies can be passed to the optimizer
- The fastest generated strategy is returned
- The strategy search returns a valid result
- The command-line search components work correctly

The complete test suite contains:

    42 tests

All tests pass.

---

# 21. Test Structure

The project now contains:

    tests/
    ├── test_track.py
    ├── test_tire.py
    ├── test_stint.py
    ├── test_pit_stop.py
    ├── test_race.py
    ├── test_strategy.py
    ├── test_optimizer.py
    ├── test_generator.py
    └── test_strategy_search.py

This provides coverage across the complete simulation and optimization pipeline.

---

# 22. Software Engineering Concepts

V5 introduces several important software-engineering concepts.

### Separation of concerns

Strategy generation and strategy optimization are independent components.

### Reusability

The same optimizer can be used with manually created or automatically generated strategies.

### Combinatorial generation

Python is used to systematically generate candidate combinations.

### Validation

Generated strategies must satisfy race constraints.

### Modular architecture

The strategy search is composed of multiple independent modules.

### Automated testing

Every major component is tested independently.

### Command-line execution

The project can be executed as a Python module.

---

# 23. Python Concepts

V5 uses several important Python concepts.

### `itertools.product`

Used to generate Cartesian products of tire compounds.

Conceptually:

    product(TireCompound, repeat=2)

produces every possible pair.

### Nested iteration

Compound combinations and stint-length combinations are combined using nested loops.

### List creation

Generated strategies are stored in a list for later evaluation.

### Type hints

The project continues using type annotations such as:

    list[RaceStrategy]

### Modules

The project is divided into separate Python modules with clear responsibilities.

### `__main__`

The command-line runner uses:

    if __name__ == "__main__":

to execute the application when the module is run directly.

---

# 24. Version Progression

## V1 — Basic Race Simulator

    Track
      ↓
    Constant lap time
      ↓
    Race time

Purpose:

Create the basic race simulation framework.

---

## V2 — Tire Degradation

    Track
      +
    Tire
      ↓
    Changing lap times

Purpose:

Introduce tire compounds, tire age, and degradation.

---

## V3 — Pit Stops and Race Strategy

    Track
      +
    RaceStrategy
       │
       ├── Stint
       ├── PitStop
       └── Stint
      ↓
    Race time

Purpose:

Represent multi-stint race strategies.

---

## V4 — Strategy Optimization

    Manually created strategies
            ↓
    StrategyOptimizer
            ↓
    Compare race times
            ↓
    Fastest strategy

Purpose:

Automatically select the fastest strategy from supplied candidates.

---

## V5 — Automatic Strategy Generation

    Race parameters
            ↓
    StrategyGenerator
            ↓
    Generate candidate strategies
            ↓
    StrategyOptimizer
            ↓
    Fastest strategy

Purpose:

Automatically search a defined strategy space.

---

# 25. V5 Architecture

The complete V5 architecture is:

    ┌─────────────────────┐
    │    Race Parameters  │
    │                     │
    │  Number of laps     │
    │  Base lap time      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  StrategyGenerator  │
    │                     │
    │ Compound choices    │
    │ Stint-length splits │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ Candidate Strategies│
    │                     │
    │ Strategy 1           │
    │ Strategy 2           │
    │ ...                  │
    │ Strategy N           │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  StrategyOptimizer  │
    │                     │
    │ Evaluate candidates │
    │ Find minimum time   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │   Fastest Strategy  │
    └─────────────────────┘

---

# 26. Example Workflow

Assume:

    Race length = 6 laps
    Base lap time = 90 seconds

The generator creates:

    45 strategies

The optimizer evaluates them.

A candidate might be:

    Soft → Hard
    3 laps → 3 laps

Another might be:

    Medium → Soft
    2 laps → 4 laps

Another:

    Hard → Medium
    5 laps → 1 lap

All candidates are evaluated.

The optimizer returns the candidate with the lowest simulated race time.

---

# 27. What V5 Can Now Answer

V1 could answer:

> How long does this race take?

V2 could answer:

> How does tire degradation affect race time?

V3 could answer:

> How fast is this particular race strategy?

V4 could answer:

> Which of these manually supplied strategies is fastest?

V5 can answer:

> Which strategy is fastest among all strategies in the defined search space?

This is a significant improvement in the project's capability.

---

# 28. Limitations

V5 is still a simplified strategy-search system.

### Fixed pit-stop duration

Every generated strategy currently uses the same pit-stop duration.

### Fixed number of stints

Only two-stint strategies are currently generated.

### Simplified tire model

Tire performance is based on the existing simplified degradation model.

### Constant baseline pace

The base lap time remains constant.

### No fuel model

Fuel load is not simulated.

### No weather

Weather and track-condition changes are not included.

### No traffic

Traffic and overtaking are not modeled.

### No historical data

The simulator does not yet use real F1 race data.

### No machine learning

The current system is deterministic rather than ML-based.

---

# 29. Why V5 Is Important for the Final Project

V5 establishes the basic optimization pipeline required for a more advanced F1 race-strategy system.

The project now has:

    Simulation
        ↓
    Strategy representation
        ↓
    Strategy generation
        ↓
    Strategy optimization

This provides a strong foundation for introducing more realistic race variables.

Eventually, the architecture can become:

    Race Conditions
          │
          ├── Track
          ├── Weather
          ├── Fuel
          ├── Tire state
          └── Traffic
                ↓
        Race Simulation
                ↓
        Candidate Strategies
                ↓
        Strategy Evaluation
                ↓
        Optimization
                ↓
       Recommended Strategy

---

# 30. Future Development

## V6 — More Realistic Race Simulation

Potential additions:

- Fuel consumption
- Fuel-mass effect
- More realistic pit-stop modeling
- Track temperature
- Air temperature
- Weather
- Safety-car periods
- Variable lap times
- More realistic tire degradation

The goal of V6 will be to improve the simulation model rather than simply increasing the number of generated strategies.

---

## V7 — Historical F1 Data

Introduce real race data.

Potential data:

- Lap times
- Tire compounds
- Tire age
- Pit stops
- Weather
- Track conditions
- Driver positions
- Race results

The data can be used to calibrate and validate the simulation.

---

## V8 — Machine Learning

Machine learning can then be introduced to predict race behavior.

Possible prediction targets:

- Lap time
- Tire degradation
- Pit-stop loss
- Race pace
- Stint performance

The ML model could provide predictions to the strategy optimizer.

---

# 31. Long-Term Architecture

The long-term goal is:

    Historical Race Data
             ↓
    Data Processing
             ↓
    Machine Learning Model
             ↓
    Predicted Race Behavior
             ↓
    Strategy Generator
             ↓
    Strategy Simulator
             ↓
    Strategy Optimizer
             ↓
    Recommended Race Strategy

V5 establishes the Strategy Generator and automated search components required for this architecture.

---

# 32. Final V5 Status

Version:

    V5 — Automatic Strategy Generation and Search

Status:

    Complete

Tests:

    42 passed

Main capabilities:

    ✓ Track simulation
    ✓ Tire compounds
    ✓ Tire degradation
    ✓ Multiple stints
    ✓ Pit stops
    ✓ Race strategies
    ✓ Strategy validation
    ✓ Strategy optimization
    ✓ Automatic tire-compound generation
    ✓ Automatic stint-length generation
    ✓ Automatic candidate-strategy generation
    ✓ Exhaustive strategy search
    ✓ Fastest strategy selection
    ✓ Repeatable optimization
    ✓ Command-line strategy search
    ✓ Automated unit testing
    ✓ Versioned documentation

V5 represents the transition from a manually configured strategy simulator to an automated strategy-search system.

The next major development stage is:

    V6 — More Realistic Race Simulation

The focus of V6 should be on improving the realism of the race model rather than simply generating more strategies.