# Version 1.0 — Basic F1 Race Simulator

## 1. Objective

The goal of Version 1 is to establish the software architecture and mathematical foundation for an F1 race simulation.

The simulator models:

- A race track
- Average vehicle speed
- Lap time
- Number of race laps
- Total race duration

This version deliberately uses a simplified model. The purpose is not to reproduce a real F1 race yet, but to create a clean foundation that can be progressively extended.

---

## 2. Concepts Learned

### 2.1 Object-Oriented Modeling

The real-world problem contains several different entities.

For example:

- A track has a length.
- A track has a number of race laps.
- A race takes place on a track.
- A race has a total duration.

Instead of representing everything as unrelated variables, we model these entities as software objects.

The current model therefore contains:

```text
Track
├── name
├── length
├── number of laps
└── average speed

Race
└── Track
```

This is an example of using **object-oriented programming (OOP)** to represent a real-world system.

---

### 2.2 Separation of Responsibilities

An important software-design principle is that different classes should have different responsibilities.

The `Track` class is responsible for information and calculations related to the track.

The `Race` class is responsible for calculations related to the race.

For example:

```python
track.lap_time_seconds()
```

belongs to the `Track` model because lap time depends on track length and average speed.

On the other hand:

```python
race.total_race_time_seconds()
```

belongs to the `Race` model because total race duration depends on the number of laps.

This separation will become increasingly important as the simulator becomes more complex.

---

### 2.3 Composition

The `Race` class contains a `Track` object.

This relationship can be represented as:

```text
Track
  ↑
  │
contains
  │
Race
```

More precisely:

```python
class Race:
    def __init__(self, track: Track):
        self.track = track
```

This is called **composition**.

The important idea is:

> A Race has a Track.

It is not:

> A Race is a Track.

This distinction is important when designing object-oriented software.

---

## 3. Design Decisions

### 3.1 Why Use Separate `Track` and `Race` Classes?

One possible implementation would be to create a single large class:

```text
Race
├── track name
├── track length
├── number of laps
├── average speed
└── race calculations
```

This would work for a small program.

However, it would mix two different concepts:

- The physical characteristics of a track
- The characteristics of a race event

Instead, we use:

```text
Track
   ↓
Race
```

where a `Race` contains a `Track`.

This keeps the responsibilities separated and makes the architecture easier to extend.

For example, later we can have:

```text
Race
├── Track
├── Car
├── Driver
├── TireSet
└── Strategy
```

without putting all of those concepts into one enormous class.

---

### 3.2 Why Composition Instead of Inheritance?

We could theoretically make:

```text
Race inherits from Track
```

However, inheritance represents an **"is-a" relationship**.

For example:

```text
Dog is an Animal
```

makes sense.

But:

```text
Race is a Track
```

does not make conceptual sense.

Instead:

```text
Race has a Track
```

is correct.

Therefore, composition is more appropriate than inheritance here.

This is an example of choosing a software-design approach based on the relationship between real-world concepts rather than simply using inheritance because it is available.

---

## 4. Mathematical Model

### 4.1 Lap Time

The basic relationship between distance, speed and time is:

```text
time = distance / speed
```

The track length is stored in kilometres and the average speed is stored in kilometres per hour.

Therefore:

```text
lap_time_hours = length_km / speed_kmh
```

To convert hours into seconds:

```text
lap_time_seconds = (length_km / speed_kmh) × 3600
```

For example, for:

```text
Track length = 5 km
Average speed = 200 km/h
```

we obtain:

```text
lap_time_seconds = (5 / 200) × 3600
                 = 90 seconds
```

---

### 4.2 Total Race Time

Version 1 assumes that every lap takes exactly the same amount of time.

Therefore:

```text
total_race_time = lap_time × number_of_laps
```

For a 50-lap race:

```text
total_race_time = 90 × 50
                = 4500 seconds
```

which corresponds to:

```text
4500 / 60 = 75 minutes
```

---

## 5. Why Is the Model So Simple?

A real F1 race does not have constant lap times.

A simplified example might look like:

```text
Lap 1    91.2 s
Lap 2    90.8 s
Lap 3    90.7 s
...
Lap 15   92.1 s
Lap 16   92.5 s
...
Pit stop
...
Lap 17   89.3 s
```

Lap times can change because of many factors, including:

- Tire compound
- Tire degradation
- Tire temperature
- Fuel load
- Track evolution
- Weather
- Traffic
- Driver performance
- Car performance
- Pit stops

We intentionally ignore these factors in Version 1.

The purpose is to establish a simple and understandable baseline before introducing additional complexity.

This illustrates an important modeling principle:

> Start with a simple model that can be understood and tested, then progressively add complexity.

---

## 6. Model Assumptions

Version 1 makes the following assumptions:

1. Vehicle speed is constant.
2. Every lap has the same lap time.
3. Fuel load does not affect performance.
4. Tires do not degrade.
5. There are no pit stops.
6. Weather remains constant.
7. There is no traffic.
8. Driver performance remains constant.
9. Car performance remains constant.
10. Track characteristics are represented only by total track length.

These assumptions make the model easy to understand but significantly reduce its realism.

---

## 7. Input Validation

The `Track` class validates its input parameters.

The following conditions are required:

```text
track length > 0
number of laps > 0
average speed > 0
```

For example, a track with:

```text
length = -5 km
```

is physically meaningless.

Instead of allowing invalid data into the simulation, the `Track` class raises a `ValueError`.

### Why Validate Inputs?

Simulation models can produce misleading results if invalid parameters are allowed.

This becomes especially important later when the simulation generates training data for machine learning.

The desired workflow is:

```text
Input validation
       ↓
Simulation
       ↓
Valid data
       ↓
Machine Learning
```

rather than:

```text
Invalid input
       ↓
Incorrect simulation
       ↓
Incorrect training data
       ↓
Incorrect ML model
```

Therefore, input validation is part of maintaining the quality of the eventual ML dataset.

---

## 8. Testing

Automated testing is implemented using `pytest`.

The current tests verify:

### Track Creation

Checks that a `Track` object correctly stores its parameters.

### Lap-Time Calculation

Checks that the mathematical model produces the expected result.

### Total Race-Time Calculation

Checks that the `Race` class correctly calculates total race duration.

### Input Validation

Tests verify that invalid values for:

- Track length
- Number of laps
- Average speed

are rejected.

The current test result is:

```text
6 passed
```

---

## 9. Why Use Automated Testing?

One option would be to run the program manually and inspect the output.

For example:

```text
Track: Demo Circuit
Lap time: 90 seconds
Race time: 4500 seconds
```

However, this does not automatically tell us whether the calculations remain correct after modifying the code.

Automated tests provide a repeatable way of checking expected behavior.

The development workflow is therefore:

```text
Change code
    ↓
Run tests
    ↓
All tests pass?
   / \
 Yes  No
  ↓    ↓
Continue  Investigate
```

As the simulator becomes more complex, automated testing becomes increasingly important.

---

## 10. Current Architecture

The current architecture is:

```text
                ┌──────────────┐
                │    Track     │
                ├──────────────┤
                │ name         │
                │ length       │
                │ laps         │
                │ average speed│
                └──────┬───────┘
                       │
                       │ contains
                       ▼
                ┌──────────────┐
                │     Race     │
                ├──────────────┤
                │ Track        │
                │              │
                │ total time   │
                └──────────────┘
```

The source code is separated from the tests:

```text
src/
└── f1_strategy/
    └── simulation/
        ├── track.py
        └── race.py

tests/
├── test_track.py
└── test_race.py
```

---

## 11. Limitations

The current simulator cannot yet answer meaningful race-strategy questions.

For example, it cannot determine:

> Should the driver start on soft or medium tires?

or:

> When should the driver pit?

This is because the current model assumes every lap is identical.

The most important missing component is therefore **time-varying vehicle performance**.

---

## 12. What We Learned

After completing Version 1, the following concepts have been introduced:

- Python package structure
- `pyproject.toml`
- Virtual environments
- Editable package installation
- Object-oriented modeling
- Classes and objects
- Composition
- Separation of responsibilities
- Derived quantities
- Mathematical modeling
- Input validation
- Unit testing with `pytest`
- Test-driven verification of model behavior

The most important modeling principle introduced in this version is:

> **Build a simple, understandable model first, then add complexity progressively.**

---

## 13. Next Version

Version 2 will introduce **tire and race dynamics**.

The simulator will move from:

```text
Constant lap time
```

towards:

```text
Lap 1
  ↓
Tire state
  ↓
Fuel state
  ↓
Lap time
  ↓
Updated tire/fuel state
  ↓
Lap 2
  ↓
...
```

The first new physical effect will be **tire degradation**.

We will initially implement a simple model and then investigate more realistic alternatives, such as nonlinear degradation.

This will introduce the concept of a **stateful simulation**, where the result of one lap affects the conditions of the next lap.