# V3 — Pit Stops and Multiple Tire Stints

## 1. Overview

Version 3 extends the race simulator from a single tire run into a basic race strategy simulator.

V2 could simulate tire degradation over a race, but the race used one tire set for the entire simulation.

V3 introduces:

- Multiple tire stints
- Pit stops
- Race strategies
- Explicit ordering of stints and pit stops
- Race-length validation

The goal is to represent a strategy such as:

    Medium
        ↓
    20 laps
        ↓
    Pit stop
        ↓
    Hard
        ↓
    30 laps

The simulator can then calculate the total race time of that strategy.

---

## 2. Evolution from V2

### V2

The architecture was approximately:

    Race
    │
    ├── Track
    │
    └── Tire

The same tire was used throughout the race.

### V3

The architecture becomes:

    Race
    │
    ├── Track
    │
    └── RaceStrategy
          │
          ├── Stint
          │     └── Tire
          │           └── TireCompound
          │
          ├── PitStop
          │
          └── Stint
                └── Tire
                      └── TireCompound

This allows the simulator to represent different tire strategies.

---

## 3. Project Structure

The relevant structure is:

    f1-race-strategy-ml/
    │
    ├── docs/
    │   ├── V1_basic_race_simulator.md
    │   ├── V2_tire_degradation_model.md
    │   └── V3_pit_stops_and_strategy.md
    │
    ├── src/
    │   └── f1_strategy/
    │       └── simulation/
    │           ├── race.py
    │           ├── pit_stop.py
    │           ├── stint.py
    │           ├── strategy.py
    │           ├── tire.py
    │           └── track.py
    │
    ├── tests/
    │   ├── test_pit_stop.py
    │   ├── test_race.py
    │   ├── test_stint.py
    │   ├── test_strategy.py
    │   ├── test_tire.py
    │   └── test_track.py
    │
    ├── pyproject.toml
    └── .gitignore

---

## 4. Stints

A stint represents a continuous period of racing on one tire set.

For example:

    Stint
    ├── Tire: Medium
    └── Laps: 20

The `Stint` class contains:

    tire
    number_of_laps

A stint is responsible for simulating its own laps.

---

## 5. Stint Simulation

The main method is:

    total_time_seconds(base_lap_time)

For every lap in the stint:

    1. Calculate tire performance
    2. Calculate lap time
    3. Add lap time to total
    4. Age the tire

Conceptually:

    total_time = 0

    repeat for every stint lap:

        lap_time =
            base_lap_time
            + tire performance delta

        total_time += lap_time

        tire.age_one_lap()

    return total_time

This reuses the tire model developed in V2.

---

## 6. Why Create a Stint Class?

Without a `Stint` class, `Race` would need to directly manage:

- tire state
- tire degradation
- lap counting
- switching tires
- pit stops

That would make `Race` increasingly complicated.

Instead:

    Tire
    → manages tire state

    Stint
    → manages continuous laps on one tire

    PitStop
    → represents a pit-stop time penalty

    RaceStrategy
    → combines stints and pit stops

    Race
    → executes the strategy on a track

This separation makes the system easier to extend.

---

## 7. Pit Stops

V3 introduces the `PitStop` class.

A pit stop currently contains:

    duration_seconds

For example:

    PitStop(20.0)

represents a 20-second pit-stop penalty.

The class provides:

    time_seconds()

which returns the pit-stop duration.

---

## 8. Pit Stop Validation

A pit stop must have a positive duration.

Therefore:

    PitStop(20.0)

is valid.

But:

    PitStop(0.0)

and:

    PitStop(-5.0)

are rejected.

This is another example of a domain constraint.

---

## 9. Race Strategy

The most important architectural addition in V3 is `RaceStrategy`.

A race strategy represents the sequence of tire stints and pit stops.

For example:

    Medium stint
        ↓
    Pit stop
        ↓
    Hard stint

The corresponding objects are:

    RaceStrategy
    ├── Stint(Medium)
    ├── PitStop
    └── Stint(Hard)

---

## 10. Strategy Ordering

A strategy with two stints requires one pit stop:

    Stint → PitStop → Stint

A strategy with three stints requires two pit stops:

    Stint → PitStop → Stint → PitStop → Stint

Therefore:

    number of stints =
        number of pit stops + 1

This relationship is enforced when creating `RaceStrategy`.

An invalid strategy such as:

    1 stint
    1 pit stop

is rejected.

---

## 11. Why Does the Strategy Own the Sequence?

An important design decision was made in V3.

Instead of having:

    Race
    ├── list of stints
    └── list of pit stops

the race now receives:

    Race
    └── RaceStrategy

This is more expressive.

The strategy represents an actual race decision.

For example:

    Strategy A

    Soft
      ↓
    Pit
      ↓
    Hard


    Strategy B

    Medium
      ↓
    Pit
      ↓
    Hard


    Strategy C

    Soft
      ↓
    Pit
      ↓
    Medium
      ↓
    Pit
      ↓
    Hard

Later, these strategies can be compared.

---

## 12. Race Responsibility

The `Race` class is now deliberately simple.

It contains:

    Track
    RaceStrategy

Its main responsibility is to calculate the total race time.

Conceptually:

    Race
      ↓
    Track provides baseline lap time
      ↓
    RaceStrategy executes the strategy
      ↓
    Strategy calculates stint and pit-stop time
      ↓
    Total race time

This keeps strategy logic outside the race itself.

---

## 13. Race Calculation

For a strategy:

    Medium
    3 laps
    ↓
    Pit stop
    20 seconds
    ↓
    Hard
    3 laps

the calculation is:

    Medium stint
    + Pit stop
    + Hard stint

For a baseline lap time of 90 seconds:

    Medium:
    89.50 + 89.55 + 89.60
    = 268.65 s

    Hard:
    90.00 + 90.03 + 90.06
    = 270.09 s

    Pit stop:
    20.00 s

    Total:
    268.65
    + 270.09
    + 20.00
    = 558.74 s

---

## 14. Race-Length Validation

A strategy must cover the complete race.

For example:

    Race length = 6 laps

Valid:

    Stint 1 = 3 laps
    Stint 2 = 3 laps

    Total = 6 laps

Invalid:

    Stint 1 = 2 laps
    Stint 2 = 3 laps

    Total = 5 laps

Also invalid:

    Stint 1 = 4 laps
    Stint 2 = 4 laps

    Total = 8 laps

The `Race` class therefore validates:

    strategy.total_laps()
        ==
    track.number_of_laps

If the values do not match, a `ValueError` is raised.

---

## 15. Domain Invariants

V3 introduces several important invariants.

### Tire age

    age >= 0

### Stint length

    number_of_laps > 0

### Pit-stop duration

    duration_seconds > 0

### Strategy structure

    number_of_stints =
        number_of_pit_stops + 1

### Race coverage

    total strategy laps =
        total race laps

These constraints prevent physically or logically invalid race configurations.

---

## 16. Testing

The V3 test suite contains:

### Track

- Track creation
- Lap-time calculation
- Invalid track length
- Invalid lap count
- Invalid average speed

### Tire

- Tire compounds
- Tire age
- Tire aging
- Tire validation
- Compound parameters
- Tire degradation

### Stint

- Stint time calculation
- Tire aging during stint
- Invalid stint length

### PitStop

- Pit-stop duration
- Invalid zero duration
- Invalid negative duration

### RaceStrategy

- Strategy time calculation
- Strategy structure validation
- Single-stint strategy

### Race

- Multiple-stint race calculation
- Independent tire aging
- Race-length validation

Total:

    27 tests

All tests currently pass.

---

## 17. Testing Strategy

The tests are designed to verify behavior rather than implementation details.

For example:

    assert total_time == 558.74

verifies that the complete strategy produces the expected race time.

Another test verifies:

    first_tire.age == 3
    second_tire.age == 3

This confirms that each stint modifies its own tire state.

The tests therefore act as executable specifications for the simulation model.

---

## 18. Current Limitations

V3 is still a simplified race simulator.

### Pit stops are fixed-duration

Every pit stop currently has a manually supplied duration.

Real pit-stop time depends on:

- pit lane
- team
- stationary time
- pit entry and exit
- race conditions

### No strategy optimization

The user must manually define the strategy.

The simulator does not yet answer:

    Which strategy is fastest?

### No fuel model

Fuel load is not modeled.

### No weather

Weather conditions are not considered.

### No safety car

Safety-car periods are not modeled.

### No traffic

Cars do not interact with each other.

### No track evolution

Grip changes are not modeled.

### Simplified tire degradation

The degradation model remains linear.

---

## 19. What V3 Demonstrates

### Python

- Classes
- Objects
- Enums
- Type hints
- Exceptions
- Lists
- Iteration
- Object composition

### Software Engineering

- Separation of responsibilities
- Domain modeling
- Domain invariants
- Encapsulation
- Reusable components
- Unit testing

### Simulation

- State transitions
- Multi-stage simulation
- Sequential events
- Parameterized behavior

### Project Engineering

- Python packaging
- Virtual environments
- pytest
- Git
- GitHub
- Versioned documentation

---

## 20. Architecture After V3

The current architecture is:

    Track
      │
      └── baseline lap time
               │
               ▼
            Race
               │
               ▼
        RaceStrategy
          │       │
          │       └── PitStop
          │
          ├── Stint
          │     └── Tire
          │           └── TireCompound
          │
          └── Stint
                └── Tire
                      └── TireCompound

The important abstraction is:

    Race
    → executes a strategy

    RaceStrategy
    → defines what the strategy is

    Stint
    → defines a period on one tire

    Tire
    → defines tire state

    TireCompound
    → defines compound characteristics

    PitStop
    → defines pit-stop time

    Track
    → defines baseline track performance

---

## 21. Version Progression

### V1 — Basic Race Simulator

    Track
      ↓
    Constant lap time
      ↓
    Race time

### V2 — Tire Degradation

    Track
      +
    Tire
      ↓
    Changing lap times

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

### V4 — Strategy Comparison

The next version will introduce the ability to compare different strategies.

For example:

    Strategy A
    Medium → Hard

    Strategy B
    Soft → Hard

    Strategy C
    Soft → Medium → Hard

The simulator will calculate the total time of each strategy.

The goal becomes:

    Find the fastest strategy

This is the first step toward an actual race-strategy optimization system.

---

## 22. V3 Learning Summary

The main lesson of V3 is that a race strategy can be modeled as a sequence of domain objects.

Instead of representing the strategy as a collection of numbers, we represent:

    Stint
    PitStop
    Stint

This makes the software closer to the actual problem domain.

The architecture is also becoming easier to extend.

Future versions can add:

    Fuel
    Weather
    Safety car
    Traffic
    Driver performance
    Track evolution
    Strategy optimization
    Historical F1 data
    Machine learning

without requiring the entire simulator to be rewritten.

---

## 23. Final V3 Status

Version:

    V3 — Pit Stops and Multiple Tire Stints

Status:

    Complete

Tests:

    27 passed

Main capabilities:

    ✓ Tire degradation
    ✓ Multiple tire stints
    ✓ Pit stops
    ✓ Race strategies
    ✓ Strategy validation
    ✓ Race-length validation
    ✓ Automated tests
    ✓ Technical documentation

The next milestone is:

    V4 — Strategy Comparison and Optimization