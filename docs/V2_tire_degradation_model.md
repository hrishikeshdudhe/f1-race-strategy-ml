# V2 — Tire Degradation Race Model

## 1. Overview

Version 2 extends the basic race simulator from V1 by introducing tire compounds, tire age, tire degradation, and lap-by-lap race simulation.

The purpose of this version is to move from a race model with a constant lap time toward a simple model in which lap performance changes as the tires wear.

The model is intentionally simplified. It does not attempt to reproduce real Formula 1 tire behavior. Instead, it provides a controlled software model that can later be extended with more realistic data and strategy logic.

---

## 2. What Changed from V1

### V1

In V1, race time was calculated using:

    Total race time = lap time × number of laps

Every lap was assumed to have the same duration.

For example:

    90 s/lap × 50 laps = 4500 s

### V2

V2 replaces this constant-lap-time assumption with a lap-by-lap simulation.

Each lap is affected by the current tire state:

    Track
      ↓
    Baseline lap time
      ↓
    Tire performance effect
      ↓
    Actual lap time
      ↓
    Tire ages
      ↓
    Next lap

Therefore, lap time can change throughout the race.

---

## 3. Project Structure

The relevant project structure is:

    f1-race-strategy-ml/
    │
    ├── docs/
    │   ├── V1_basic_race_simulator.md
    │   └── V2_tire_degradation_model.md
    │
    ├── src/
    │   └── f1_strategy/
    │       └── simulation/
    │           ├── race.py
    │           ├── tire.py
    │           └── track.py
    │
    ├── tests/
    │   ├── test_race.py
    │   ├── test_tire.py
    │   └── test_track.py
    │
    ├── pyproject.toml
    └── .gitignore

---

## 4. Tire Compound Model

The first major addition is the `TireCompound` enum.

The three compounds currently modeled are:

    SOFT
    MEDIUM
    HARD

Each compound contains three pieces of information:

    Compound
    ├── label
    ├── pace_offset
    └── degradation_rate

The implementation is:

    class TireCompound(Enum):
        SOFT = ("soft", -1.0, 0.08)
        MEDIUM = ("medium", -0.5, 0.05)
        HARD = ("hard", 0.0, 0.03)

The values are intentionally simplified and are not intended to represent real-world Formula 1 tire data.

They provide relative behavior:

    Soft
    → fastest initially
    → highest degradation

    Medium
    → intermediate initial pace
    → intermediate degradation

    Hard
    → slowest initially
    → lowest degradation

---

## 5. Why Are the Parameters Stored in the Enum?

One design option would have been to store the parameters inside every `Tire` object.

For example:

    class Tire:
        self.pace_offset = ...
        self.degradation_rate = ...

However, these properties describe the compound itself rather than an individual tire.

A Soft tire set should use the Soft compound characteristics.

Therefore, the model separates:

    TireCompound
    → static compound characteristics

    Tire
    → state of an individual tire

This avoids unnecessary duplication and gives each class a clearer responsibility.

---

## 6. Tire State

A `Tire` represents an individual tire set being used during a race.

It currently contains:

    Tire
    ├── compound
    └── age

For example:

    Tire
    ├── compound = MEDIUM
    └── age = 5

The tire age represents the number of completed laps.

A newly installed tire therefore has:

    age = 0

After one completed lap:

    age = 1

After five completed laps:

    age = 5

---

## 7. Tire Age Validation

Negative tire age is not physically meaningful.

Therefore the constructor rejects negative values:

    if age < 0:
        raise ValueError("Tire age cannot be negative")

This introduces the concept of a domain constraint.

Not every integer is a valid tire age.

Valid:

    0
    1
    2
    3
    ...

Invalid:

    -1
    -2
    ...

---

## 8. Tire State Transition

The `Tire` class contains:

    def age_one_lap(self) -> None:
        self.age += 1

This represents the state transition caused by completing one lap.

Conceptually:

    Before lap:
    age = 4

    Lap completed

    After lap:
    age = 5

The simulation therefore changes the state of the tire as the race progresses.

---

## 9. Tire Performance Model

The tire performance effect is modeled using:

    ΔT = pace_offset + degradation_rate × age

Where:

- `ΔT` = tire contribution to lap time
- `pace_offset` = initial performance advantage/disadvantage of the compound
- `degradation_rate` = lap-time penalty added per completed lap
- `age` = number of completed laps on the tire

The complete lap-time equation is:

    Lap time = baseline lap time + tire performance delta

---

## 10. Example of the Tire Model

Consider a Medium tire:

    pace_offset = -0.50 s
    degradation_rate = 0.05 s/lap

For a new tire:

    age = 0

    ΔT = -0.50 + (0.05 × 0)
       = -0.50 s

If the baseline lap time is 90 seconds:

    Lap time = 90.00 - 0.50
             = 89.50 s

After one completed lap:

    age = 1

    ΔT = -0.50 + (0.05 × 1)
       = -0.45 s

    Lap time = 89.55 s

After five completed laps:

    age = 5

    ΔT = -0.50 + (0.05 × 5)
       = -0.25 s

    Lap time = 89.75 s

Therefore, the tire becomes progressively slower as it ages.

---

## 11. Why Does the Tire Return a Performance Delta?

The `Tire` class provides:

    def performance_delta(self) -> float:
        return (
            self.compound.pace_offset
            + self.compound.degradation_rate * self.age
        )

The method returns only the tire's contribution to lap time rather than calculating the complete lap time.

This is a deliberate separation of responsibilities.

The tire does not need to know:

- the track length
- the average speed
- the baseline lap time
- the number of race laps

Instead:

    Tire
    → calculates tire effect

    Track
    → calculates baseline lap time

    Race
    → combines them

This makes the components easier to understand and modify independently.

---

## 12. Race Simulation

V1 calculated race time directly:

    lap_time * number_of_laps

This is no longer possible because every lap can have a different tire performance.

V2 therefore simulates each lap individually.

The conceptual algorithm is:

    total_time = 0

    for every lap:
        calculate tire performance
        calculate lap time
        add lap time to total
        age tire

    return total_time

The implementation is:

    def total_race_time_seconds(self) -> float:
        total_time = 0.0

        for _ in range(self.track.number_of_laps):
            lap_time = (
                self.track.lap_time_seconds()
                + self.tire.performance_delta()
            )

            total_time += lap_time
            self.tire.age_one_lap()

        return total_time

---

## 13. Order of Operations

The order of operations is important.

For every lap:

1. Calculate current tire performance
2. Calculate lap time
3. Add lap time to total
4. Complete the lap
5. Increase tire age

For example:

    Start
    Tire age = 0

        ↓

    Calculate Lap 1 using age 0

        ↓

    Lap completed

        ↓

    Tire age = 1

        ↓

    Calculate Lap 2 using age 1

        ↓

    Lap completed

        ↓

    Tire age = 2

This follows the definition that tire age represents completed laps.

A newly installed tire therefore does not receive a degradation penalty before completing its first lap.

---

## 14. Object Composition

The `Race` object now contains both a `Track` and a `Tire`.

Conceptually:

    Race
    ├── Track
    └── Tire

This is an example of object composition.

The `Race` object does not inherit from `Track` or `Tire`.

Instead, it uses instances of those classes.

This allows each object to maintain a focused responsibility.

---

## 15. Separation of Responsibilities

The current architecture can be summarized as:

    Track
    │
    └── Provides baseline lap time

    TireCompound
    │
    └── Provides compound characteristics

    Tire
    │
    ├── Stores tire state
    ├── Stores compound
    ├── Tracks tire age
    └── Calculates tire performance effect

    Race
    │
    ├── Combines Track and Tire
    ├── Simulates individual laps
    └── Calculates total race time

This separation is important because the project will become significantly more complex in later versions.

For example, future versions can add:

    Weather
    Fuel
    Pit stops
    Driver performance
    Traffic
    Safety cars
    Track evolution
    Strategy decisions

without requiring all of these responsibilities to be placed inside a single class.

---

## 16. Alternative Design Approaches

Several other designs could have been used.

### 16.1 Store tire parameters directly in `Tire`

Example:

    class Tire:
        self.pace_offset = ...
        self.degradation_rate = ...

Advantages:

- Simple
- Easy to understand

Disadvantages:

- Compound properties are duplicated across tire objects
- More difficult to manage many compounds
- Less clear separation between compound definition and tire state

The current design was preferred because compound characteristics are shared properties.

---

### 16.2 Use a Dictionary for Compound Parameters

Another approach would be:

    COMPOUND_PROPERTIES = {
        TireCompound.SOFT: {
            "pace_offset": -1.0,
            "degradation_rate": 0.08,
        }
    }

Advantages:

- Flexible
- Easy to modify externally
- Can work well for configuration-driven models

Disadvantages:

- More indirect
- More opportunities for missing keys
- Compound properties are separated from the enum

This approach may become useful later if the model parameters need to come from configuration files or real data.

---

### 16.3 Use a Dedicated Data Class

A more advanced architecture could use a separate object representing compound characteristics.

For example:

    TireCompound
          ↓
    CompoundProperties
          ↓
        Tire

This provides more flexibility but would introduce additional complexity.

For V2, that complexity is unnecessary.

---

## 17. Testing

V2 contains tests for:

### Tire compounds

- Compounds exist
- Compound labels are correct
- Compound parameters are correct
- Compound performance relationships are correct

### Tire state

- New tires start at age 0
- Tires can start with an existing age
- Tire age increases after a lap
- Negative age is rejected

### Tire performance

- New tire performance is correct
- Tire performance changes with age
- Performance worsens as tire age increases

### Race simulation

- Race time includes tire performance
- Tire age increases during the race

The project currently contains:

    17 passing tests

---

## 18. Testing Behavior Rather Than Implementation

The tests generally focus on observable behavior.

For example:

    assert new_delta > initial_delta

tests the domain behavior:

    An older tire should be slower.

It does not require a specific implementation.

This is preferable to testing internal implementation details because the implementation may change while the expected behavior remains the same.

---

## 19. Known Limitations

The V2 model is intentionally simplified.

### Tire degradation is linear

The model assumes:

    degradation = constant × age

Real tire degradation can be nonlinear and can depend on many factors.

### Compound parameters are manually defined

The current values:

    Soft   = -1.0 s, 0.08 s/lap
    Medium = -0.5 s, 0.05 s/lap
    Hard   =  0.0 s, 0.03 s/lap

are synthetic values.

They are not real Formula 1 measurements.

### No weather

The model assumes constant conditions.

### No fuel effect

Real Formula 1 cars become lighter as fuel is consumed, affecting lap time.

V2 does not model this.

### No driver differences

Every race uses the same performance model.

### No pit stops

The race currently uses one tire for the entire race.

### Race simulation mutates tire state

Calling:

    race.total_race_time_seconds()

ages the tire.

Calling the same method again therefore does not reproduce the exact same initial race state.

This is acceptable for the current simplified model but is a limitation that should be addressed when the simulator becomes more sophisticated.

---

## 20. What V2 Demonstrates

This version demonstrates knowledge of:

### Python

- Classes
- Objects
- Type hints
- Enums
- Methods
- Exceptions
- Iteration

### Software Engineering

- Separation of responsibilities
- Object composition
- Domain modeling
- State management
- Unit testing
- Test-driven refinement

### Simulation

- State transitions
- Iterative simulation
- Mathematical modeling
- Parameterized behavior

### Project Engineering

- Python packaging
- Virtual environments
- pytest
- Git
- GitHub
- Technical documentation

---

## 21. Why V2 Matters for the Final F1 Project

The eventual goal is not simply to calculate lap times.

The final project will need to answer questions such as:

- Should the driver start on Soft or Medium?
- When should the driver pit?
- Would a one-stop strategy be faster than a two-stop strategy?
- How does tire degradation affect the optimal strategy?
- What happens if a safety car occurs?
- Which strategy minimizes total race time?

V2 provides the foundation for these questions.

The progression is:

    V1
    Basic race calculation
        ↓
    V2
    Tire degradation
        ↓
    V3
    Pit stops and multiple tire stints
        ↓
    V4
    Race strategy simulation
        ↓
    V5
    Data-driven prediction
        ↓
    V6
    Machine learning
        ↓
    Final Project
    F1 Race Strategy Prediction & Simulation

---

## 22. Key Learning Takeaways

### 1. Model the domain

Instead of treating tires as numbers, we created a `Tire` object with meaningful state and behavior.

### 2. Separate static properties from changing state

Compound characteristics belong to `TireCompound`.

Tire age belongs to `Tire`.

### 3. Encapsulate behavior

The tire calculates its own performance effect through:

    performance_delta()

The race does not need to know the degradation equation.

### 4. Simulations require state transitions

The tire changes after each completed lap.

### 5. Tests should verify behavior

Tests protect the expected domain behavior while allowing implementation details to evolve.

### 6. Avoid premature complexity

The model is intentionally simple.

More sophisticated architecture will be introduced when the project actually requires it.

---

## 23. Next Version

The next major version will introduce:

    V3 — Pit Stops and Multiple Tire Stints

The race will no longer be restricted to a single tire set.

A strategy could become:

    Start
      │
      ▼
    Medium
      │
      │ 20 laps
      ▼
    Pit stop
      │
      ▼
    Hard
      │
      │ 30 laps
      ▼
    Finish

This will allow us to calculate:

    Total race time
    +
    Pit-stop time
    +
    Multiple tire stints

This is the point where the project starts becoming an actual race strategy simulator rather than only a tire degradation simulator.