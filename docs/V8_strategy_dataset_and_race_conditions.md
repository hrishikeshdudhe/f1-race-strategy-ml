# V8 — Strategy Constraints, Race Conditions, Strategy Analysis, and Dataset Generation

## 1. Overview

Version 8 was a major expansion of the F1 Race Strategy ML project.

The earlier versions established the core race simulation, including:

- tracks,
- tires,
- stints,
- pit stops,
- fuel,
- race strategies,
- strategy generation,
- and race-time calculation.

V8 builds a higher-level strategy analysis and dataset-generation layer on top of that simulation.

The main objective of V8 was to make the simulator capable of:

1. generating constrained strategies,
2. evaluating strategies,
3. ranking strategies,
4. producing detailed strategy results,
5. modeling changing race conditions,
6. calculating race-condition effects,
7. comparing strategies,
8. generating datasets,
9. generating datasets from multiple configurations,
10. exporting the results to CSV,
11. and preparing the project for the future machine-learning stage.

The final V8 test checkpoint was:

```text
204 passed, 0 failed
```

This is the baseline that should be preserved before starting V9.

---

# 2. V8 Development Philosophy

The main principle during V8 was:

> Add new functionality without breaking functionality from earlier versions.

This became especially important because V8 introduced several new abstractions:

```text
StrategyConstraints
StrategyResult
StrategyResults
RaceCondition
RaceConditionSchedule
StrategyDatasetGenerator
MultiConfigurationDataset
```

Instead of replacing previous interfaces completely, backward-compatible interfaces were retained where possible.

For example, the optimizer retained the existing `evaluate()` and `find_fastest()` behavior while adding detailed evaluation and ranking.

Similarly, `StrategyResult` became a structured object while retaining tuple-style access through `__getitem__`.

---

# 3. V8 Starting Point

At the beginning of V8, the project already contained the core simulation components:

```text
fuel.py
pit_stop.py
race.py
stint.py
strategy.py
tire.py
track.py
generator.py
optimizer.py
```

The simulator could already represent race strategies and calculate their total race time.

However, the project did not yet have a complete framework for:

- strategy constraints,
- structured strategy results,
- strategy ranking,
- race-condition schedules,
- race-condition metrics,
- dataset generation,
- multiple race configurations,
- and CSV dataset export.

V8 therefore expanded the existing simulator into a more complete simulation-analysis-data pipeline.

---

# 4. Strategy Constraints

## 4.1 Motivation

The first major V8 addition was a dedicated strategy constraint system.

The purpose was to allow the strategy generator to work with explicit requirements instead of generating unrestricted strategies only.

The new module was:

```text
src/f1_strategy/simulation/constraints.py
```

The main class is:

```python
StrategyConstraints
```

The constraint system supports:

- minimum stint length,
- maximum stint length,
- minimum number of pit stops,
- maximum number of pit stops,
- required tire compounds.

---

# 5. StrategyConstraints

A constraint object can describe rules such as:

```python
StrategyConstraints(
    minimum_stint_laps=2,
    maximum_stint_laps=5,
    minimum_pit_stops=1,
    maximum_pit_stops=2,
    required_compounds={
        TireCompound.MEDIUM,
        TireCompound.HARD,
    },
)
```

All constraints are optional.

This was important because the existing project behavior must remain unchanged when constraints are not provided.

Therefore:

```python
StrategyConstraints()
```

represents an unrestricted strategy configuration.

---

# 6. Default Constraint Values

The V8 tests explicitly checked the default constraint values.

Unspecified restrictions use `None`.

For example:

```python
minimum_stint_laps = None
maximum_stint_laps = None
```

means that there is no minimum or maximum imposed by the constraint object.

Likewise, an unspecified pit-stop limit does not restrict the number of pit stops.

This makes the constraint system flexible enough to be used incrementally.

---

# 7. Stint-Length Validation

The constraints system introduced:

```python
is_stint_length_valid(...)
```

This method checks whether a stint satisfies the configured minimum and maximum.

For example:

```text
minimum = 2
maximum = 5
```

gives:

```text
1 lap  → invalid
2 laps → valid
3 laps → valid
5 laps → valid
6 laps → invalid
```

If either limit is `None`, that side of the comparison is ignored.

This prevents errors when only one limit is configured.

---

# 8. Pit-Stop Validation

V8 also introduced:

```python
is_pit_stop_count_valid(...)
```

This checks whether a strategy contains an allowed number of pit stops.

For example:

```python
StrategyConstraints(
    minimum_pit_stops=1,
    maximum_pit_stops=2,
)
```

means:

```text
0 pit stops → invalid
1 pit stop   → valid
2 pit stops  → valid
3 pit stops  → invalid
```

Again, `None` means that no restriction is imposed on that side.

---

# 9. Required Compound Validation

The constraints system also introduced:

```python
are_compounds_valid(...)
```

This checks whether a strategy contains all required tire compounds.

For example:

```python
StrategyConstraints(
    required_compounds={
        TireCompound.MEDIUM,
        TireCompound.HARD,
    }
)
```

requires the strategy to contain both:

```text
MEDIUM
HARD
```

A strategy such as:

```text
MEDIUM → HARD
```

is valid.

A strategy such as:

```text
MEDIUM → SOFT
```

is invalid because HARD is missing.

---

# 10. Compound Validation Bug

During development, the following test initially failed:

```python
assert constraints.are_compounds_valid(stints)
```

The strategy contained:

```text
MEDIUM
HARD
```

and both compounds were required, but the method returned:

```text
False
```

The validation logic was corrected to inspect the actual compounds used by the stints.

After the correction, the compound validation tests passed.

This was one of the first examples of the V8 development approach:

```text
Add feature
    ↓
Write tests
    ↓
Find implementation mismatch
    ↓
Fix implementation
    ↓
Run complete suite
```

---

# 11. Constraint-Aware Strategy Generation

The next step was integrating `StrategyConstraints` into `StrategyGenerator`.

The generator can now be configured conceptually as:

```python
StrategyGenerator(
    number_of_laps=6,
    constraints=constraints,
)
```

The generator creates candidate strategies and checks whether they satisfy the configured constraints.

The constraint checks therefore become part of strategy generation.

---

# 12. Constraint Filtering

Generated strategies can be filtered using:

```text
stint length
pit-stop count
required tire compounds
```

This allows different datasets to be generated for different strategy rules.

For example, a dataset could require:

```text
at least one pit stop
minimum stint length of two laps
MEDIUM compound must be used
HARD compound must be used
```

The generator will reject strategies that do not satisfy those requirements.

---

# 13. Preserving Previous Generator Behavior

A very important part of V8 was preserving earlier behavior.

Adding constraints must not unintentionally change the strategy count when no constraints are supplied.

During development, a regression was found in the generator.

The expected behavior for the existing two-stint generation path had to be preserved.

This was tested repeatedly while the constraint system was developed.

The final implementation ensures that:

```python
StrategyGenerator(
    number_of_laps=6
)
```

continues to follow the established generation behavior.

The important design decision was:

> Constraint handling should be an additional capability, not an accidental rewrite of the existing strategy-generation algorithm.

---

# 14. StrategyResult

The next major V8 component was:

```text
src/f1_strategy/simulation/strategy_result.py
```

with:

```python
StrategyResult
```

The motivation was to replace a simple:

```python
(strategy, total_time)
```

representation with a richer result object.

The result object stores:

```text
strategy
total_time_seconds
rank
time_delta_seconds
time_gap_to_next_seconds
```

This gives the project one central place for strategy-analysis metrics.

---

# 15. StrategyResult — Basic Data

The constructor supports:

```python
StrategyResult(
    strategy=strategy,
    total_time_seconds=time,
    rank=None,
    time_delta_seconds=0.0,
    time_gap_to_next_seconds=0.0,
)
```

The ranking-related fields are initially optional because a strategy can first be evaluated and ranked later.

---

# 16. Pit-Stop Metrics

`StrategyResult` provides:

```python
pit_stop_time_seconds
```

which calculates the total time spent in pit stops.

It also provides:

```python
number_of_pit_stops
```

which returns the number of pit stops in the strategy.

This means pit-stop information can be accessed directly from the result rather than repeatedly navigating through the underlying strategy object.

---

# 17. Stint Metrics

The result object provides:

```python
total_laps
number_of_stints
stint_laps
```

For example, a strategy with:

```text
3 laps MEDIUM
3 laps HARD
```

has:

```text
total_laps = 6
number_of_stints = 2
stint_laps = [3, 3]
```

---

# 18. Tire Strategy Metrics

The result object provides:

```python
tire_compounds
```

which contains the tire compound labels used by the stints.

It also provides:

```python
tire_strategy
```

which converts the compounds into a readable representation.

For example:

```text
MEDIUM -> HARD
```

This representation is particularly useful for CSV exports and human-readable reports.

---

# 19. Average Lap Time

V8 added:

```python
average_lap_time_seconds
```

The metric is calculated as:

```text
total race time / total laps
```

If the strategy contains zero laps, the implementation returns:

```text
0.0
```

instead of attempting a division by zero.

---

# 20. Strategy Performance Gaps

Three important ranking metrics were introduced:

```python
time_delta_seconds
time_gap_percentage
time_gap_to_next_seconds
```

### Time delta

The time delta represents how much slower a strategy is than the fastest strategy.

The fastest strategy has:

```text
time_delta_seconds = 0
```

### Time-gap percentage

This expresses the difference relative to the fastest race time.

### Gap to next

This represents the difference between a strategy and the strategy immediately ahead of it in the ranking.

The final strategy has:

```text
time_gap_to_next_seconds = 0.0
```

because there is no strategy after it.

---

# 21. StrategyResult Summary

A human-readable:

```python
summary()
```

method was added.

The summary includes information such as:

```text
Rank
Total race time
Time difference
Time gap
Gap to next
Average lap time
Stints
Stint laps
Tires
Pit stops
Pit-stop time
```

This makes it easier to inspect an individual strategy without manually printing every property.

---

# 22. StrategyResult Backward Compatibility

A major compatibility problem appeared after introducing `StrategyResult`.

Existing tests and code expected tuple-style access.

For example:

```python
result[0]
result[1]
```

The new object initially caused:

```text
TypeError: 'StrategyResult' object is not subscriptable
```

To preserve compatibility, `StrategyResult` was given:

```python
__getitem__(...)
```

with the following behavior:

```python
result[0]
```

returns:

```text
strategy
```

and:

```python
result[1]
```

returns:

```text
total_time_seconds
```

Any other index raises:

```text
IndexError
```

This allowed the richer result model to coexist with older tuple-based expectations.

---

# 23. StrategyResults Collection

V8 introduced:

```text
src/f1_strategy/simulation/strategy_results.py
```

with:

```python
StrategyResults
```

The purpose of this class is to represent a collection of `StrategyResult` objects.

Instead of repeatedly passing around:

```python
list[StrategyResult]
```

the project can use a dedicated collection abstraction.

This became especially useful for:

- ranking results,
- CSV export,
- summary/report functionality,
- strategy comparison,
- and dataset generation.

---

# 24. StrategyOptimizer Expansion

The optimizer was significantly expanded in:

```text
src/f1_strategy/simulation/optimizer.py
```

The optimizer already evaluated strategies.

V8 extended it with:

```python
evaluate_detailed(...)
rank_strategies(...)
rank_strategies_collection(...)
```

while retaining:

```python
evaluate(...)
find_fastest(...)
```

for compatibility.

---

# 25. Detailed Strategy Evaluation

The new:

```python
evaluate_detailed(...)
```

returns:

```python
list[StrategyResult]
```

rather than simple tuples.

This makes detailed strategy analysis possible.

The basic `evaluate()` method remains available and returns the previous tuple-style structure:

```python
(strategy, total_time)
```

This separation was intentional.

---

# 26. Safe Strategy Copying

The optimizer evaluates a copied version of each strategy.

The internal method:

```python
_copy_strategy(...)
```

creates independent copies of:

- stints,
- tires,
- pit stops,
- fuel.

This is important because evaluating or ranking strategies should not modify the original strategies supplied to the optimizer.

The test suite specifically checks that ranking does not modify the original strategies.

This prevents subtle bugs when the same generated strategies are reused for:

- comparison,
- ranking,
- reporting,
- or dataset generation.

---

# 27. Strategy Ranking

V8 introduced:

```python
rank_strategies(...)
```

The ranking process is:

```text
Input strategies
       ↓
Evaluate each strategy
       ↓
Create StrategyResult objects
       ↓
Sort by total race time
       ↓
Assign rank
       ↓
Calculate time delta
       ↓
Calculate gap to next
       ↓
Return ranked results
```

The fastest strategy is always:

```text
rank = 1
```

and:

```text
time_delta_seconds = 0
```

---

# 28. Ranking Implementation

Strategies are sorted using total race time:

```python
sorted(
    results,
    key=lambda result: result.total_time_seconds,
)
```

After sorting, ranks are assigned starting at:

```text
1
```

The fastest time is stored and used to calculate the time delta for every other strategy.

For example:

```text
Fastest strategy = 550.00 s
Strategy B       = 552.50 s
```

then:

```text
Strategy B time delta = 2.50 s
```

---

# 29. Gap to Next Strategy

After ranking, each result is compared to the next result.

For example:

```text
Rank 1 = 550.00 s
Rank 2 = 551.20 s
Rank 3 = 554.00 s
```

produces:

```text
Rank 1 gap to next = 1.20 s
Rank 2 gap to next = 2.80 s
Rank 3 gap to next = 0.00 s
```

This provides additional information about how tightly strategies are grouped.

---

# 30. Ranking Collection

The optimizer also provides:

```python
rank_strategies_collection(...)
```

This calls:

```python
rank_strategies(...)
```

and wraps the result in:

```python
StrategyResults
```

This became the interface used by the dataset-generation layer.

---

# 31. Race Conditions

Another major V8 feature was race-condition modeling.

The new module is:

```text
src/f1_strategy/simulation/race_condition.py
```

It contains:

```python
RaceCondition
```

implemented as an enum.

The supported conditions are:

```text
GREEN
YELLOW
VSC
SAFETY_CAR
```

---

# 32. RaceCondition Values

Each race condition has:

```text
label
lap_time_multiplier
```

The implemented values are:

| Condition | Label | Multiplier |
|---|---|---:|
| GREEN | green | 1.00 |
| YELLOW | yellow | 1.10 |
| VSC | vsc | 1.20 |
| SAFETY_CAR | safety_car | 1.30 |

The multiplier represents the increase in lap time caused by the race condition.

---

# 33. RaceCondition Properties

The enum provides:

```python
condition.label
```

to retrieve the textual label.

It also provides:

```python
condition.lap_time_multiplier
```

to retrieve the numerical multiplier.

For example:

```python
RaceCondition.VSC.label
```

returns:

```text
vsc
```

and:

```python
RaceCondition.VSC.lap_time_multiplier
```

returns:

```text
1.20
```

---

# 34. RaceConditionSchedule

The second race-condition component is:

```text
src/f1_strategy/simulation/race_condition_schedule.py
```

with:

```python
RaceConditionSchedule
```

Its purpose is to assign race conditions to individual laps.

The constructor takes:

```python
RaceConditionSchedule(
    number_of_laps=...
)
```

and uses:

```text
GREEN
```

as the default condition.

---

# 35. Setting Race Conditions

A race-condition range can be configured using:

```python
schedule.set_condition(
    start_lap=3,
    end_lap=4,
    condition=RaceCondition.VSC,
)
```

This assigns:

```text
Lap 3 → VSC
Lap 4 → VSC
```

Every lap in the requested range is explicitly stored.

---

# 36. Default Race Condition

If a lap does not have a special condition assigned, the schedule returns the default condition.

By default:

```text
GREEN
```

is used.

For example, with a six-lap race:

```text
Lap 1 → GREEN
Lap 2 → GREEN
Lap 3 → VSC
Lap 4 → VSC
Lap 5 → GREEN
Lap 6 → GREEN
```

This means only the affected laps need to be explicitly configured.

---

# 37. RaceConditionSchedule Validation

The schedule validates the race and lap boundaries.

The following are invalid:

```text
number_of_laps <= 0
start_lap < 1
end_lap < start_lap
end_lap > number_of_laps
```

For example:

```python
RaceConditionSchedule(number_of_laps=6)
```

cannot accept:

```python
set_condition(
    start_lap=4,
    end_lap=7,
    condition=RaceCondition.VSC,
)
```

because lap 7 is outside the six-lap race.

---

# 38. Querying a Condition

The condition assigned to a particular lap can be retrieved using:

```python
schedule.condition_for_lap(lap_number)
```

The method validates that the requested lap belongs to the race.

An invalid lap number raises:

```text
ValueError
```

---

# 39. Race Conditions in Strategy Evaluation

`StrategyOptimizer` was extended so that it can receive:

```python
race_condition_schedule
```

For example:

```python
StrategyOptimizer(
    base_lap_time=90.0,
    race_condition_schedule=schedule,
)
```

The schedule is then passed into the race-time calculation.

Therefore the race time is no longer necessarily based on one constant lap-time condition.

Each lap can have its own condition.

---

# 40. Race-Condition Effect on Lap Time

The race condition multiplier modifies the base lap time.

For example:

```text
Base lap time = 90 s
```

Under VSC:

```text
90 × 1.20 = 108 s
```

The additional delay is:

```text
108 - 90 = 18 s
```

Similarly:

```text
Yellow:
90 × 1.10 = 99 s

Safety Car:
90 × 1.30 = 117 s
```

This creates deterministic race-condition effects suitable for testing and dataset generation.

---

# 41. Race-Condition Details in StrategyResult

V8 expanded the strategy-result layer to expose race-condition information.

The detailed result functionality covers information such as:

```text
condition lap counts
condition delay
condition summary
```

This makes it possible to determine not only how fast a strategy was, but also why the simulated race time changed.

---

# 42. Condition Lap Counts

A strategy result can determine how many laps were affected by each race condition.

Conceptually:

```text
Green laps
Yellow laps
VSC laps
Safety Car laps
```

This is useful as future ML input data because the number of laps under each condition can influence race performance.

---

# 43. Condition Delay

The result layer calculates the additional time caused by non-green conditions.

For example:

```text
Base lap time = 90 s
VSC multiplier = 1.20
```

gives:

```text
VSC lap time = 108 s
VSC delay = 18 s
```

If several VSC laps occur, the delays are accumulated.

---

# 44. Floating-Point Precision Issue

One race-condition test initially produced:

```text
17.999999999999996
```

instead of:

```text
18.0
```

This is a normal floating-point representation issue.

The mathematical result is still:

```text
18.0
```

The test was therefore changed to use approximate numerical comparison rather than exact floating-point equality.

The final test passed with the mathematically expected result.

This is an important testing lesson for the project:

> Floating-point simulation values should generally be compared with an appropriate tolerance.

---

# 45. Race-Condition Summary

A readable condition summary was also introduced.

The summary records condition labels together with their lap numbers.

For example:

```text
vsc:3;green:4;green:5;green:6
```

can describe the conditions associated with the relevant laps.

This representation is compact and can also be stored in the generated dataset.

---

# 46. Behavior Without a Race-Condition Schedule

The result system was explicitly tested for the case where no race-condition schedule is provided.

Without a schedule, the result should behave as a normal race result.

The condition-specific metrics should not incorrectly report race incidents.

This preserves the behavior of earlier versions while allowing race-condition analysis when a schedule is supplied.

---

# 47. Dataset Generation

V8 introduced:

```text
src/f1_strategy/simulation/dataset.py
```

The main class is:

```python
StrategyDatasetGenerator
```

The purpose is to combine:

```text
strategy generation
+
strategy evaluation
+
strategy ranking
```

into a dataset-oriented workflow.

---

# 48. StrategyDatasetGenerator Configuration

The constructor accepts:

```text
number_of_laps
base_lap_time
initial_fuel_mass_kg
fuel_consumption_per_lap_kg
race_condition_schedule
```

Conceptually:

```python
StrategyDatasetGenerator(
    number_of_laps=6,
    base_lap_time=90.0,
    initial_fuel_mass_kg=100.0,
    fuel_consumption_per_lap_kg=1.8,
    race_condition_schedule=schedule,
)
```

The fuel parameters are optional so that the generator remains compatible with configurations that do not use explicit fuel modeling.

---

# 49. Dataset Strategy Generation

The method:

```python
generate_strategies()
```

creates a `StrategyGenerator` using the configured race parameters.

It then calls:

```python
generate_two_stint_strategies()
```

and returns the generated strategies.

The dataset generator therefore does not implement a separate strategy-generation algorithm.

Instead, it reuses the existing simulation component.

This avoids duplication.

---

# 50. Dataset Strategy Evaluation

The method:

```python
evaluate_strategies()
```

performs the following:

```text
Create StrategyGenerator
        ↓
Generate strategies
        ↓
Create StrategyOptimizer
        ↓
Evaluate strategies
        ↓
Rank strategies
        ↓
Return StrategyResults
```

The optimizer receives the configured:

```text
base_lap_time
race_condition_schedule
```

so the generated dataset reflects the requested race configuration.

---

# 51. Dataset CSV Export

The method:

```python
export_csv(file_path)
```

evaluates the strategies and then exports the resulting `StrategyResults`.

This provides a direct way to create a machine-readable dataset from the simulation.

---

# 52. Configuration Serialization

`StrategyDatasetGenerator` provides:

```python
configuration()
```

which returns its configuration as a dictionary.

The stored information includes:

```text
number_of_laps
base_lap_time
initial_fuel_mass_kg
fuel_consumption_per_lap_kg
race_condition_schedule
```

This makes configurations explicit and reusable.

---

# 53. Configuration Reconstruction

The class also provides:

```python
from_configuration(...)
```

as a class method.

It can recreate a `StrategyDatasetGenerator` from a configuration dictionary.

Conceptually:

```text
Configuration dictionary
        ↓
from_configuration()
        ↓
StrategyDatasetGenerator
```

This is useful when multiple dataset configurations need to be stored and processed consistently.

---

# 54. MultiConfigurationDataset

V8 introduced:

```python
MultiConfigurationDataset
```

This allows multiple race configurations to be evaluated together.

The constructor accepts:

```python
configurations: list[dict]
```

and requires at least one configuration.

An empty configuration list raises:

```text
ValueError
```

---

# 55. Generating Multiple Results

The method:

```python
generate_results()
```

loops through every configuration.

For each configuration it:

1. creates a `StrategyDatasetGenerator`,
2. reconstructs it using `from_configuration()`,
3. evaluates the strategies,
4. stores the resulting `StrategyResults`.

The output is therefore:

```python
list[StrategyResults]
```

with one result collection per configuration.

---

# 56. Total Strategy Count

The multi-configuration dataset provides:

```python
total_strategy_count()
```

This calculates the total number of strategy results across all configurations.

Conceptually:

```text
Configuration 1 → N strategies
Configuration 2 → N strategies
Configuration 3 → N strategies

Total = N + N + N
```

This provides a quick way to determine the size of the generated dataset.

---

# 57. Multi-Configuration CSV Export

`MultiConfigurationDataset` also provides:

```python
export_csv(file_path)
```

All configurations are exported into one CSV file.

Each row contains a:

```text
configuration_id
```

so rows can be traced back to their originating race configuration.

This is important for machine-learning datasets because the configuration itself can become part of the feature set.

---

# 58. Dataset CSV Columns

The V8 dataset export contains the following columns:

```text
configuration_id
number_of_laps
base_lap_time
race_condition
rank
total_time_seconds
time_delta_seconds
time_gap_percentage
time_gap_to_next_seconds
average_lap_time_seconds
total_laps
number_of_stints
number_of_pit_stops
pit_stop_time_seconds
tire_strategy
stint_laps
```

These columns combine:

```text
race configuration
+
strategy characteristics
+
performance metrics
```

---

# 59. Configuration ID

The:

```text
configuration_id
```

identifies which race configuration produced the row.

The ID is assigned according to the configuration's position in the supplied configuration list.

For example:

```text
configuration 0
configuration 1
configuration 2
```

can be distinguished even if the generated strategies have identical structures.

---

# 60. Race Configuration Columns

The dataset records:

```text
number_of_laps
base_lap_time
```

These describe the basic race environment.

Fuel configuration is part of the generator configuration and can be used when building the underlying strategy simulation.

Race-condition information is stored separately.

---

# 61. Race Condition CSV Representation

The `race_condition` column stores the configured lap conditions as a compact string.

For example:

```text
vsc:3;green:4;green:5;green:6
```

This records the condition and lap association.

During development, a test checked for:

```text
VSC:3
```

while the exported value contained:

```text
vsc:3
```

The discrepancy was resolved by aligning the expected representation with the actual enum label representation.

The canonical labels in `RaceCondition` are lowercase:

```text
green
yellow
vsc
safety_car
```

Therefore the CSV uses those labels.

---

# 62. Rank Column

The:

```text
rank
```

column stores the position of the strategy after ranking.

The fastest strategy receives:

```text
rank = 1
```

Higher numbers represent slower strategies.

This makes rank a direct target candidate for future machine-learning experiments.

---

# 63. Total Time

The:

```text
total_time_seconds
```

column contains the complete simulated race time.

This includes the effects represented by the simulator, such as:

- lap times,
- tire effects,
- fuel effects,
- pit stops,
- and race conditions.

It is one of the most important performance targets in the generated dataset.

---

# 64. Time Delta

The:

```text
time_delta_seconds
```

column measures the difference from the fastest strategy.

The fastest strategy has:

```text
0.0
```

Every slower strategy has a positive difference.

For example:

```text
Fastest = 550.0 s
Strategy = 553.5 s

time_delta_seconds = 3.5
```

---

# 65. Time Gap Percentage

The:

```text
time_gap_percentage
```

column expresses the strategy's time difference relative to the fastest strategy.

This gives a normalized comparison that can be useful when comparing races of different lengths.

---

# 66. Gap to Next Strategy

The:

```text
time_gap_to_next_seconds
```

column contains the time difference between the current strategy and the next ranked strategy.

The last strategy receives:

```text
0.0
```

because there is no next strategy.

---

# 67. Average Lap Time Column

The:

```text
average_lap_time_seconds
```

column contains:

```text
total race time / total laps
```

This gives a normalized performance measure.

---

# 68. Strategy Structure Columns

The dataset also contains:

```text
total_laps
number_of_stints
number_of_pit_stops
pit_stop_time_seconds
```

These describe the structure of the strategy and its pit-stop cost.

---

# 69. Tire Strategy Column

The:

```text
tire_strategy
```

column stores the tire sequence.

For example:

```text
MEDIUM -> HARD
```

This provides a human-readable representation of the strategy's compound sequence.

---

# 70. Stint Laps Column

The:

```text
stint_laps
```

column stores the number of laps in each stint.

For example:

```text
3,3
```

represents:

```text
Stint 1 → 3 laps
Stint 2 → 3 laps
```

This allows the ML dataset to preserve the actual strategy structure instead of storing only its final race time.

---

# 71. Strategy Comparison Infrastructure

Additional V8 tests and result functionality were added around strategy comparison.

The purpose was to make it possible to compare strategies based on:

- total race time,
- time difference,
- percentage gap,
- gap to the next strategy,
- pit-stop time,
- average lap time,
- tire strategy,
- and stint structure.

This provides the analytical foundation required before introducing an ML model.

---

# 72. Strategy Reports and Summaries

V8 also expanded the reporting layer around strategy results.

The result summary provides a compact textual representation that can be used for debugging or inspecting simulation output.

The information includes:

```text
Rank
Total race time
Time difference
Time gap
Gap to next
Average lap time
Stints
Stint laps
Tires
Pit stops
Pit-stop time
```

This helps verify the simulation results before they are written into datasets.

---

# 73. Test Suite Expansion

V8 significantly expanded the automated test suite.

The important V8 test files include:

```text
tests/test_constraints.py
tests/test_dataset.py
tests/test_generator_constraints.py
tests/test_optimizer_detailed.py
tests/test_strategy_comparison.py
tests/test_strategy_comparison_metrics.py
tests/test_strategy_ranking.py
tests/test_strategy_report.py
tests/test_strategy_result.py
tests/test_strategy_result_details.py
tests/test_strategy_result_summary.py
tests/test_strategy_results.py
tests/test_strategy_results_csv.py
```

These tests cover the new functionality as well as compatibility with previous behavior.

---

# 74. Constraint Tests

`test_constraints.py` checks:

```text
default values
valid stint lengths
invalid stint lengths
valid pit-stop counts
invalid pit-stop counts
valid required compounds
invalid required compounds
```

These tests establish the expected behavior of the constraint layer independently of the strategy generator.

---

# 75. Generator Constraint Tests

`test_generator_constraints.py` verifies that constraints actually affect generated strategies.

The tests ensure that:

```text
invalid stint lengths
invalid pit-stop counts
missing required compounds
```

are excluded from the generated strategy set.

They also ensure that unrestricted generation retains its previous behavior.

---

# 76. Optimizer Tests

The optimizer tests cover:

```text
detailed evaluation
strategy ranking
fastest strategy
ranking order
race-condition effects
preservation of original strategies
```

This ensures that the optimizer remains deterministic and side-effect free.

---

# 77. Strategy Result Tests

The strategy-result tests verify:

```text
total race time
pit-stop metrics
stint metrics
tire metrics
average lap time
time gaps
summary
tuple-style access
```

The detailed result tests additionally cover race-condition information.

---

# 78. Race-Condition Tests

The race-condition tests verify:

```text
default GREEN behavior
explicit condition assignment
lap-range assignment
invalid lap ranges
condition retrieval
race-condition delay
condition counts
condition summary
behavior without a schedule
```

These tests are important because race-condition behavior affects the final dataset.

---

# 79. Dataset Tests

The dataset tests verify:

```text
dataset generator construction
strategy generation
strategy evaluation
CSV export
configuration reconstruction
multi-configuration generation
total strategy count
configuration IDs
race-condition export
```

This ensures that the final dataset layer is connected correctly to the simulation.

---

# 80. Development Test Progress

V8 was developed incrementally.

During the implementation, the test count progressed through several checkpoints.

The project reached:

```text
121 passed
127 passed
132 passed
136 passed
141 passed
148 passed
152 passed
162 passed
168 passed
175 passed
181 passed
188 passed
```

Additional functionality was then added and tested.

Later checkpoints included:

```text
199 passed
203 passed
204 passed
```

The purpose of recording these checkpoints was to ensure that new functionality was being added without losing previously working behavior.

---

# 81. Important Intermediate Failures

The V8 development process included several real test failures.

These failures were useful because they identified interface and design problems.

Some of the major failures were:

```text
StrategyConstraints default-value mismatch
missing is_stint_length_valid()
missing is_pit_stop_count_valid()
missing are_compounds_valid()
```

These were fixed by completing the constraints interface.

---

# 82. Optimizer API Failure

The optimizer initially lacked:

```python
rank_strategies(...)
```

Several ranking tests failed with:

```text
AttributeError:
'StrategyOptimizer' object has no attribute 'rank_strategies'
```

The ranking method was then implemented.

---

# 83. StrategyResult Compatibility Failure

After introducing `StrategyResult`, several optimizer tests failed with:

```text
TypeError:
'StrategyResult' object is not subscriptable
```

This happened because older tests expected:

```python
result[0]
result[1]
```

The solution was to implement `__getitem__()` in `StrategyResult`.

This restored backward compatibility while retaining the richer result model.

---

# 84. RaceStrategy Construction Failure

Some new tests initially created a `RaceStrategy` without a valid pit-stop configuration.

The project correctly enforces the relationship:

```text
number of stints = number of pit stops + 1
```

For example:

```text
2 stints → 1 pit stop
3 stints → 2 pit stops
```

The tests were corrected so that the strategies they constructed represented valid race strategies.

This was preferable to weakening the core `RaceStrategy` validation merely to accommodate the test.

---

# 85. Floating-Point Test Failure

The condition-delay test produced:

```text
17.999999999999996
```

while the expected mathematical result was:

```text
18.0
```

The issue was not with the simulation formula.

It was caused by floating-point representation.

The test was therefore changed to use an approximate comparison.

The final behavior was accepted as mathematically correct.

---

# 86. Dataset Race-Condition Export Failure

The dataset test also caught a representation mismatch.

The test expected:

```text
VSC:3
```

while the exported enum label was:

```text
vsc:3
```

The final representation follows the canonical `RaceCondition.label` values.

Therefore the CSV uses:

```text
green
yellow
vsc
safety_car
```

rather than introducing a second inconsistent naming convention.

---

# 87. Final V8 Git Changes

At the final development stage, the Git working tree contained modified V8 files:

```text
src/f1_strategy/simulation/generator.py
src/f1_strategy/simulation/optimizer.py
```

New V8 simulation modules included:

```text
src/f1_strategy/simulation/constraints.py
src/f1_strategy/simulation/dataset.py
src/f1_strategy/simulation/strategy_result.py
src/f1_strategy/simulation/strategy_results.py
```

The V8 development also added the race-condition modules:

```text
src/f1_strategy/simulation/race_condition.py
src/f1_strategy/simulation/race_condition_schedule.py
```

---

# 88. V8 Test Files

The Git working tree also contained the V8 test additions:

```text
tests/test_constraints.py
tests/test_dataset.py
tests/test_generator_constraints.py
tests/test_optimizer_detailed.py
tests/test_strategy_comparison.py
tests/test_strategy_comparison_metrics.py
tests/test_strategy_ranking.py
tests/test_strategy_report.py
tests/test_strategy_result.py
tests/test_strategy_result_details.py
tests/test_strategy_result_summary.py
tests/test_strategy_results.py
tests/test_strategy_results_csv.py
```

These files collectively form the V8 validation layer.

---

# 89. Final V8 Architecture

The major V8 architecture can be represented as:

```text
                         Race Configuration
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
        Race length        Base lap time      Race conditions
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                       Strategy Constraints
                                │
                                ▼
                       Strategy Generator
                                │
                                ▼
                         Race Strategies
                                │
                                ▼
                       Strategy Optimizer
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
             Evaluation                    Ranking
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                         StrategyResult
                                │
                                ▼
                         StrategyResults
                                │
                                ▼
                    Dataset Generation Layer
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
        Single Configuration       Multiple Configurations
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                              CSV
```

---

# 90. Complete V8 Workflow

The complete V8 workflow is:

```text
1. Define race configuration
          ↓
2. Define optional constraints
          ↓
3. Define optional race-condition schedule
          ↓
4. Generate candidate strategies
          ↓
5. Apply strategy constraints
          ↓
6. Evaluate valid strategies
          ↓
7. Calculate total race time
          ↓
8. Calculate detailed strategy metrics
          ↓
9. Rank strategies
          ↓
10. Calculate time gaps
          ↓
11. Store StrategyResult objects
          ↓
12. Store results in StrategyResults
          ↓
13. Repeat for multiple configurations if required
          ↓
14. Export results to CSV
```

This is the main pipeline created by V8.

---

# 91. Why V8 Is Important for the ML Project

The project is called:

```text
f1-race-strategy-ml
```

but directly training a machine-learning model on the original simulator would be premature.

The simulator first needs a reliable way to generate many examples.

V8 establishes that infrastructure.

The simulator can now generate:

```text
Race configuration
+
Strategy
+
Race conditions
+
Strategy performance
```

for many different configurations.

That is exactly the type of structured data required for machine learning.

---

# 92. Potential ML Features

The V8 dataset infrastructure provides potential features such as:

```text
number_of_laps
base_lap_time
initial_fuel_mass_kg
fuel_consumption_per_lap_kg
tire_strategy
stint_laps
number_of_stints
number_of_pit_stops
pit_stop_time_seconds
race-condition information
condition lap counts
```

These can later be transformed into numerical features for an ML model.

---

# 93. Potential ML Targets

V8 also provides possible prediction targets.

The most important are:

```text
total_time_seconds
rank
time_delta_seconds
```

For example, a future model could attempt to predict:

```text
Expected total race time
```

or:

```text
Expected strategy rank
```

from the race configuration and strategy characteristics.

---

# 94. Why the ML Model Was Not Added Yet

V8 intentionally stops before the machine-learning model.

The goal was first to establish:

```text
Reliable simulation
        ↓
Reliable evaluation
        ↓
Reliable ranking
        ↓
Reliable dataset
```

Only after this foundation is stable should machine learning be introduced.

Otherwise, a model could learn from simulation bugs or inconsistent data.

---

# 95. V8 Design Principles

Several important software-engineering principles were reinforced during V8.

## Separation of responsibilities

Different classes now have different responsibilities:

```text
StrategyConstraints
    → decides whether strategies satisfy rules

StrategyGenerator
    → generates strategies

StrategyOptimizer
    → evaluates and ranks strategies

StrategyResult
    → represents one evaluated strategy

StrategyResults
    → represents a collection of evaluated strategies

RaceCondition
    → defines race-condition behavior

RaceConditionSchedule
    → assigns conditions to laps

StrategyDatasetGenerator
    → creates datasets from one configuration

MultiConfigurationDataset
    → combines multiple configurations
```

This keeps the architecture modular.

---

# 96. Reuse Instead of Duplication

The dataset layer does not implement another race simulator.

Instead it reuses:

```text
StrategyGenerator
StrategyOptimizer
RaceStrategy
RaceConditionSchedule
StrategyResults
```

This reduces duplicated logic.

It also means that improvements to the underlying simulator automatically become available to the dataset generator.

---

# 97. Backward Compatibility

Another major V8 principle was backward compatibility.

Examples include:

```python
StrategyOptimizer.evaluate(...)
```

remaining available.

Also:

```python
StrategyOptimizer.find_fastest(...)
```

remains available.

And:

```python
StrategyResult[0]
StrategyResult[1]
```

continues to work.

This prevents V8 from becoming an incompatible rewrite of the earlier project.

---

# 98. Testing Philosophy

The V8 development followed a test-driven/incremental approach.

The process was repeatedly:

```text
Implement a feature
        ↓
Run tests
        ↓
Inspect failures
        ↓
Fix implementation or test assumptions
        ↓
Run complete test suite
        ↓
Continue
```

The test count therefore increased progressively rather than attempting to implement the entire V8 system at once.

---

# 99. Final Test Baseline

The final V8 state reached:

```text
204 passed, 0 failed
```

This is the most important V8 completion criterion.

Before making V9 changes, run:

```bash
pytest
```

and verify that the baseline is still:

```text
204 passed
```

If the count is lower or failures appear, investigate them before beginning new V9 functionality.

---

# 100. V8 Completion Status

V8 is complete.

The project now has a complete:

```text
Simulation
    ↓
Strategy Generation
    ↓
Constraint Filtering
    ↓
Strategy Evaluation
    ↓
Race-Condition Modeling
    ↓
Strategy Ranking
    ↓
Detailed Results
    ↓
Dataset Generation
    ↓
Multi-Configuration Dataset Generation
    ↓
CSV Export
```

pipeline.

The final validated state is:

```text
204 passed
0 failed
```

---

# 101. V8 File Summary

The main V8 implementation files are:

```text
src/f1_strategy/simulation/
├── constraints.py
├── dataset.py
├── generator.py
├── optimizer.py
├── race_condition.py
├── race_condition_schedule.py
├── strategy_result.py
└── strategy_results.py
```

The existing simulation files remain:

```text
fuel.py
pit_stop.py
race.py
stint.py
strategy.py
tire.py
track.py
```

The V8 tests are located in:

```text
tests/
```

with the dedicated V8 tests described earlier.

---

# 102. Final V8 Outcome

The most important result of V8 is not simply the addition of individual classes.

V8 transformed the project from primarily being a race simulator into a system capable of generating structured strategy-performance data.

The project can now answer questions such as:

```text
Which strategy is fastest?
How much slower is another strategy?
How large is the gap to the next strategy?
How many pit stops does a strategy use?
Which compounds does it use?
How long is each stint?
How much time is caused by race conditions?
How does a race-condition schedule affect strategy performance?
Can the same analysis be repeated for many race configurations?
Can the results be exported into a machine-readable dataset?
```

These capabilities provide the foundation for the next stage of the project.

---

# 103. Transition from V8 to V9

The natural next step is to use the V8 dataset-generation infrastructure for machine learning.

The intended progression is:

```text
V8

Race simulation
      ↓
Strategy generation
      ↓
Strategy constraints
      ↓
Strategy evaluation
      ↓
Strategy ranking
      ↓
Race-condition modeling
      ↓
Dataset generation
      ↓
CSV
```

followed by:

```text
V9

Generated dataset
      ↓
Data inspection
      ↓
Feature engineering
      ↓
Train / validation / test split
      ↓
Baseline ML model
      ↓
Model evaluation
      ↓
Prediction
      ↓
Strategy recommendation
```

The V8 simulator should remain stable while the ML layer is built on top of it.

---

# 104. V8 Final Principle

The key principle to carry into V9 is:

> Keep the simulation reliable and stable while adding the machine-learning layer incrementally.

Every future change should:

1. have a clear purpose,
2. preserve existing functionality where possible,
3. include tests,
4. run the complete test suite,
5. and avoid knowingly leaving the project in a broken state.

V8 therefore serves as the stable simulation-and-dataset foundation for the machine-learning stages that follow.