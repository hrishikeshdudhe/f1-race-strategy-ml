# V7 - Race Conditions and Dynamic Race Simulation

## Overview

Version 7 extends the F1 race strategy simulator with support for changing race conditions during a race.

Previous versions assumed that every lap was driven under normal green-flag conditions. V7 introduces race conditions such as:

- Green flag
- Virtual Safety Car (VSC)
- Safety Car

The race condition can now change from lap to lap through a dedicated race-condition schedule.

This allows the simulator to represent more realistic race scenarios in which a specific range of laps is affected by an incident or neutralisation.

V7 also extends strategy generation, optimization, and strategy search so that race-condition schedules can be taken into account when evaluating strategies.

---

# Objectives

The main objectives of V7 are:

- Introduce configurable race conditions.
- Represent different lap-time effects for each race condition.
- Create a schedule describing the condition of every race lap.
- Apply the correct condition to the correct race lap.
- Support race conditions across multiple stints.
- Integrate race conditions with strategy optimization.
- Integrate race conditions with generated strategy searches.
- Preserve existing tire, fuel, pit-stop, and strategy behavior.
- Ensure that optimization does not modify the original strategy.
- Keep the simulator deterministic and testable.

---

# 1. Race Conditions

A new `RaceCondition` enumeration was introduced.

The main conditions are:

```text
GREEN
VSC
SAFETY_CAR
````

Each condition contains a lap-time multiplier.

The multiplier represents the effect of the race condition on the normal lap time.

Conceptually:

```text
Final lap time
=
Normal lap time
×
Race-condition multiplier
```

For example, under normal conditions:

```text
Normal lap time = 90.0 s
```

Under a slower race condition, the resulting lap time becomes larger.

This provides a simple abstraction for modelling neutralisations without changing the underlying tire or fuel calculations.

---

# 2. `RaceCondition`

The `RaceCondition` enum provides the available race conditions and their associated lap-time effects.

The green-flag condition acts as the baseline.

A race condition can then increase the lap time through its multiplier.

The design keeps the condition-specific behavior inside the `RaceCondition` model instead of spreading condition-specific constants throughout the simulator.

---

# 3. Race Condition Schedule

V7 introduces the `RaceConditionSchedule` class.

The schedule represents the race condition for each lap of a race.

For example, a six-lap race could have:

```text
Lap 1   GREEN
Lap 2   GREEN
Lap 3   VSC
Lap 4   VSC
Lap 5   GREEN
Lap 6   GREEN
```

A condition can be assigned to a range of laps.

Example:

```python
schedule = RaceConditionSchedule(6)

schedule.set_condition(
    start_lap=3,
    end_lap=4,
    condition=RaceCondition.VSC,
)
```

This means that laps 3 and 4 are affected by the VSC condition.

The remaining laps retain the default green-flag condition.

---

# 4. Looking Up a Lap Condition

The schedule provides a method for determining the condition of an individual race lap.

Conceptually:

```python
condition = schedule.condition_for_lap(lap_number)
```

This allows the simulation to ask:

```text
"What is the race condition on this lap?"
```

before calculating the lap time.

This is important because the race condition is associated with the overall race lap rather than with a particular stint.

---

# 5. Race Condition Validation

The race-condition schedule validates the requested race-lap range.

A condition must refer to valid laps within the race.

This prevents invalid schedules from being silently accepted.

The schedule therefore acts as the central source of truth for changing race conditions.

---

# 6. Stint Integration

The `Stint` class was extended to support race conditions.

A stint now has a default race condition:

```python
race_condition: RaceCondition = RaceCondition.GREEN
```

The stint also provides:

```python
lap_time_seconds(
    base_lap_time,
    race_condition=None,
)
```

This allows a specific race condition to be supplied for an individual lap.

If no condition is supplied, the stint's configured condition is used.

---

# 7. Lap-Time Calculation

The lap-time calculation now combines:

* Base lap time
* Tire performance
* Fuel penalty
* Race-condition multiplier

The calculation can be represented as:

```text
Normal lap time
=
Base lap time
+
Tire performance delta
+
Fuel penalty
```

Then:

```text
Final lap time
=
Normal lap time
×
Race-condition multiplier
```

Therefore, race conditions affect the complete calculated lap time.

This means that the effect of a VSC or Safety Car is applied after the normal tire and fuel effects have been calculated.

---

# 8. Lap Simulation

The `Stint` class also provides:

```python
simulate_lap(...)
```

This method calculates one lap and then updates the state.

The sequence is:

```text
Calculate lap time
        ↓
Apply race condition
        ↓
Age tire
        ↓
Consume fuel
        ↓
Return lap time
```

This maintains the stateful behavior introduced in previous versions.

For example, fuel used during one lap affects the available fuel on the next lap, while tire age increases after each completed lap.

---

# 9. Race Strategy Integration

`RaceStrategy` was extended so that race-condition schedules can be passed into the total-time calculation.

The method now supports:

```python
strategy.total_time_seconds(
    base_lap_time,
    race_condition_schedule,
)
```

The strategy tracks the overall race lap using:

```python
current_race_lap = 1
```

For every simulated lap, the strategy asks the schedule for the corresponding race condition.

Conceptually:

```text
Stint 1
    ↓
Lap 1 → condition for lap 1
Lap 2 → condition for lap 2
Lap 3 → condition for lap 3
    ↓
Pit stop
    ↓
Stint 2
    ↓
Lap 4 → condition for lap 4
Lap 5 → condition for lap 5
Lap 6 → condition for lap 6
```

This is important because race conditions must follow the race-lap number across stint boundaries.

---

# 10. Correct Conditions Across Stints

A race condition is not reset when a pit stop occurs.

For example:

```text
Race:
6 laps

Stint 1:
Laps 1-3

Pit stop

Stint 2:
Laps 4-6
```

If the Safety Car occurs on lap 4, it must affect the first lap of the second stint.

The strategy therefore maintains a separate `current_race_lap` counter rather than relying on the local lap number within a stint.

---

# 11. Fuel and Race Conditions

Race conditions work together with the fuel model.

For each lap:

```text
Current fuel
      ↓
Fuel penalty
      ↓
Tire performance
      ↓
Normal lap time
      ↓
Race-condition multiplier
      ↓
Final lap time
      ↓
Fuel consumption
```

Fuel is still shared across stints when a strategy contains a shared `Fuel` object.

A race condition does not reset or otherwise modify fuel state.

---

# 12. Tire and Race Conditions

Race conditions also work together with tire degradation.

The tire performance calculation continues to depend on tire age.

For every lap:

```text
Tire age
    ↓
Tire performance
    ↓
Race-condition effect
```

After the lap is simulated, the tire is aged by one lap.

Therefore, race conditions do not interfere with tire degradation.

---

# 13. Strategy Optimizer Integration

`StrategyOptimizer` was extended to accept an optional race-condition schedule.

The constructor now supports:

```python
StrategyOptimizer(
    base_lap_time=90.0,
    race_condition_schedule=schedule,
)
```

The optimizer passes this schedule to the strategy during evaluation.

This allows different strategies to be compared under the same race conditions.

---

# 14. Strategy Copying

The optimizer continues to evaluate copies of strategies rather than directly modifying the supplied strategies.

When a strategy is copied:

* Tires are copied.
* Fuel is copied.
* Pit stops are copied.
* Stint configuration is copied.
* Fuel penalty configuration is preserved.
* Race-condition configuration is preserved.

This is particularly important because simulation changes tire age and fuel state.

The original strategy must remain unchanged after optimization.

---

# 15. Race Condition Optimization

The optimizer can now evaluate a strategy under a race-condition schedule.

For example:

```text
Normal race:
557.33 s

Race with VSC:
> 557.33 s
```

A slower condition increases the corresponding lap time and therefore increases the total race time.

The optimizer can consequently compare strategies under more realistic race scenarios.

---

# 16. Generated Strategy Search

The generated-strategy search was also extended to accept a race-condition schedule.

The function now supports the concept of:

```python
find_fastest_generated_strategy(
    number_of_laps=6,
    base_lap_time=90.0,
    race_condition_schedule=schedule,
)
```

The flow is:

```text
StrategyGenerator
        ↓
Generate strategies
        ↓
StrategyOptimizer
        ↓
Apply race-condition schedule
        ↓
Evaluate strategies
        ↓
Find fastest strategy
```

This keeps strategy generation separate from strategy evaluation.

The generator creates possible strategies, while the optimizer determines which one performs best under the specified race conditions.

---

# 17. Example Race Scenario

Consider a six-lap race.

The race condition schedule is:

```text
Lap 1   GREEN
Lap 2   GREEN
Lap 3   VSC
Lap 4   VSC
Lap 5   GREEN
Lap 6   GREEN
```

A two-stint strategy could be:

```text
SOFT (3 laps)
        ↓
Pit stop
        ↓
HARD (3 laps)
```

The simulation applies:

```text
Lap 1 → SOFT + GREEN
Lap 2 → SOFT + GREEN
Lap 3 → SOFT + VSC
Pit stop
Lap 4 → HARD + VSC
Lap 5 → HARD + GREEN
Lap 6 → HARD + GREEN
```

This demonstrates why the overall race-lap counter is required.

---

# 18. Strategy Description

V7 also adds a human-readable description to `RaceStrategy`.

The method:

```python
strategy.description()
```

returns a compact representation of the strategy.

For example:

```text
SOFT (3 laps) → HARD (3 laps)
```

For a three-stint strategy:

```text
SOFT (2 laps) → MEDIUM (3 laps) → HARD (4 laps)
```

The description is purely informational.

It does not:

* Simulate laps.
* Age tires.
* Consume fuel.
* Change pit stops.
* Change race time.

This provides a convenient way to display generated and optimized strategies.

---

# 19. Design Structure

The V7 architecture can be summarized as:

```text
RaceCondition
      ↓
RaceConditionSchedule
      ↓
RaceStrategy
      ↓
Stint
      ↓
Tire + Fuel
```

During optimization:

```text
StrategyGenerator
        ↓
RaceStrategy objects
        ↓
StrategyOptimizer
        ↓
RaceConditionSchedule
        ↓
Race simulation
        ↓
Race time
        ↓
Fastest strategy
```

Each component has a clear responsibility.

---

# 20. Testing

V7 significantly expands the test suite.

Tests cover:

* Race-condition definitions.
* Race-condition multipliers.
* Schedule creation.
* Setting conditions for specific lap ranges.
* Looking up conditions for individual laps.
* Invalid race-condition ranges.
* Stint behavior under race conditions.
* Safety Car lap-time effects.
* VSC lap-time effects.
* Correct condition assignment to race laps.
* Race-condition behavior across multiple stints.
* Optimizer support for race-condition schedules.
* Generated strategy search with race conditions.
* Safety Car races being slower than normal races.
* Preservation of original strategies during optimization.
* Strategy descriptions.
* Multiple-stint strategy descriptions.

---

# 21. Test Development

During development, the test suite was used to identify and correct issues including:

* Floating-point precision differences.
* Race-condition schedules not being passed through the optimizer.
* Race-condition schedules not being passed through generated strategy search.
* Conditions being applied to the wrong race lap.
* Strategy copies not preserving required configuration.

The implementation was kept backward-compatible with the existing simulation functionality.

---

# 22. Final Test Status

After completing the V7 development work:

```text
96 passed
```

The test suite was then extended with additional V7 functionality and reached:

```text
99 passed
```

Later V7 development continued with additional race-condition and optimizer tests.

The important principle throughout V7 was that new functionality was added incrementally while maintaining the existing test suite.

---

# 23. Files Added or Modified

V7 introduced or extended the following simulation components:

```text
src/
└── f1_strategy/
    └── simulation/
        ├── race_condition.py
        ├── race_condition_schedule.py
        ├── race.py
        ├── stint.py
        ├── strategy.py
        ├── optimizer.py
        └── run_strategy_search.py
```

Corresponding tests include:

```text
tests/
├── test_race_condition.py
├── test_race_condition_schedule.py
├── test_stint.py
├── test_strategy.py
├── test_optimizer.py
└── test_strategy_search.py
```

---

# 24. Version Summary

V7 changes the simulator from a fixed-condition race model into a dynamic race simulation.

Before V7:

```text
Base lap time
      ↓
Tire effects
      ↓
Fuel effects
      ↓
Lap time
```

After V7:

```text
Base lap time
      ↓
Tire effects
      ↓
Fuel effects
      ↓
Race condition
      ↓
Lap time
```

The simulator can now model changing race conditions over the course of a race while retaining the existing tire, fuel, pit-stop, strategy, and optimization functionality.

---

# Status

**Version:** V7

**Main feature:** Dynamic race conditions

**Additional feature:** Human-readable strategy descriptions

**Status:** Complete

**Test suite:** Passing
