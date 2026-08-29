# V6 — Fuel and Dynamic Race Simulation

## Overview

V6 extends the F1 race strategy simulator with a simplified fuel model and dynamic lap-time calculation.

The previous versions focused on:

- Track modelling
- Tire compounds and degradation
- Stints
- Pit stops
- Race strategies
- Strategy optimization
- Automatic strategy generation

V6 introduces fuel as an additional performance factor and establishes a more detailed lap-by-lap simulation structure.

The main objective is to make the race simulation more realistic while keeping the code modular, understandable, and easy to test.

---

## 1. Goals of V6

The main goals of V6 are:

1. Model fuel as a changing race state.
2. Consume fuel after every lap.
3. Account for fuel mass when calculating lap time.
4. Share the same fuel supply across all stints of a strategy.
5. Calculate lap times explicitly on a lap-by-lap basis.
6. Give automatically generated strategies independent fuel states.
7. Maintain compatibility with the functionality developed in V1–V5.

The resulting simulation considers:

    Base lap time
          +
    Tire performance
          +
    Tire degradation
          +
    Fuel load effect
          ↓
    Simulated lap time

---

## 2. V6 Architecture

The V6 simulation can be represented as:

    Race Strategy
          |
          +-------------------+
          |                   |
       Stint 1             Stint 2
          |                   |
       Tire 1              Tire 2
          |                   |
          +---------+---------+
                    |
               Shared Fuel
                    |
              Lap-by-lap
              simulation

Fuel is treated as a continuous race state rather than being reset between stints.

---

## 3. Fuel Model

A new `Fuel` class was introduced:

    src/f1_strategy/simulation/fuel.py

The class stores:

- Initial fuel mass
- Fuel consumption per lap
- Remaining fuel mass

For example:

    Initial fuel:             100 kg
    Consumption per lap:       2 kg

    After lap 1:               98 kg
    After lap 2:               96 kg
    After lap 3:               94 kg

The fuel class provides methods for:

    consume_one_lap()
    remaining_fuel_kg()
    consumed_fuel_kg()
    copy()

Fuel validation prevents:

- Zero or negative initial fuel mass
- Zero or negative fuel consumption
- Fuel consumption greater than the initial fuel mass

---

## 4. Fuel Effect on Lap Time

Fuel mass affects the simulated lap time.

The simplified model uses:

    fuel penalty =
    remaining fuel × fuel time penalty per kg

The default fuel time penalty is:

    0.03 seconds per kilogram

For example, with 100 kg of fuel:

    100 × 0.03 = 3.0 seconds

The lap-time calculation therefore becomes:

    lap time =
    base lap time
    + tire performance delta
    + fuel penalty

As fuel is consumed, the fuel penalty decreases.

Example:

    100 kg → +3.00 s
     98 kg → +2.94 s
     96 kg → +2.88 s
     94 kg → +2.82 s

This creates a natural performance improvement as the car becomes lighter.

---

## 5. Dynamic Lap-Time Calculation

V6 introduces an explicit `lap_time_seconds()` method in the `Stint` class.

This method calculates the time for one lap using the current state of the tire and fuel.

It does not modify the state.

The state is modified only after the lap has been simulated.

The process is:

    Calculate lap time
           ↓
       Age tire
           ↓
      Consume fuel
           ↓
    Calculate next lap

This separation makes the simulation easier to extend.

Future factors such as:

- Weather
- Track evolution
- Traffic
- Safety cars
- Driver performance
- Engine modes

can be incorporated into the lap-time calculation without redesigning the complete simulation.

---

## 6. Stint Simulation

The `Stint` class now supports an optional `Fuel` object.

A stint can still be created without fuel:

    Stint(
        tire=tire,
        number_of_laps=3,
    )

This maintains compatibility with earlier versions.

A stint can also be created with fuel:

    Stint(
        tire=tire,
        number_of_laps=10,
        fuel=fuel,
    )

When fuel is present, every lap uses the current fuel mass to calculate the fuel penalty.

After each simulated lap:

    Tire age → +1
    Fuel → consumption applied

This means both tire condition and fuel load evolve during a stint.

---

## 7. Shared Fuel Across a Strategy

A major V6 improvement is that fuel is shared across the complete race strategy.

The strategy owns one fuel state:

    RaceStrategy
         |
         └── Fuel
              |
              +── Stint 1
              |
              +── Pit stop
              |
              +── Stint 2

For example:

    Initial fuel = 100 kg
    Consumption = 2 kg/lap

    Stint 1 = 3 laps
    Remaining fuel = 94 kg

    Pit stop

    Stint 2 = 3 laps
    Remaining fuel = 88 kg

The pit stop changes the tires but does not reset the fuel.

This more accurately represents the fuel behaviour of a race car.

---

## 8. Strategy Generator and Fuel

The `StrategyGenerator` was extended to optionally create fuelled strategies.

The generator now accepts:

    initial_fuel_mass_kg
    fuel_consumption_per_lap_kg

For example:

    generator = StrategyGenerator(
        number_of_laps=6,
        initial_fuel_mass_kg=100.0,
        fuel_consumption_per_lap_kg=2.0,
    )

The generator creates a separate `Fuel` object for every generated strategy.

This is important because the optimizer evaluates multiple candidate strategies.

Each strategy must therefore have independent fuel state:

    Strategy A → Fuel A
    Strategy B → Fuel B
    Strategy C → Fuel C

rather than:

    Strategy A ─┐
    Strategy B ─┼── Shared Fuel
    Strategy C ─┘

Otherwise, evaluating one strategy would modify the fuel state used by another strategy.

---

## 9. Backward Compatibility

Fuel remains optional.

Therefore, existing code from previous versions can continue to work.

For example:

    Stint(
        tire=tire,
        number_of_laps=3,
    )

still works without requiring a fuel object.

Likewise, a `RaceStrategy` can be created without explicitly providing fuel.

This allows the project to evolve incrementally rather than requiring all previous code to be rewritten.

---

## 10. Testing

V6 expanded the automated test suite.

The project currently contains:

    59 tests
    59 passed

Tests cover the following areas.

### Fuel

- Initial fuel state
- Fuel consumption
- Accumulated consumption
- Preventing negative fuel
- Invalid fuel parameters
- Fuel copying

### Stints

- Existing stint behaviour
- Tire aging
- Fuel effects
- Fuel consumption
- Dynamic single-lap calculation
- Changing lap time as fuel burns

### Strategies

- Shared fuel across stints
- Fuel not resetting at pit stops
- Existing strategy behaviour

### Strategy Generation

- Generated strategy count
- Complete race coverage
- Two-stint structure
- Fuelled strategies
- Independent fuel objects
- Fuel consumption configuration
- Invalid fuel parameters

All previous tests from V1–V5 continue to pass.

---

## 11. V6 Development Progression

V6 was developed incrementally.

### V6.1 — Fuel State

Introduced the `Fuel` class.

The class is responsible for maintaining:

- Initial fuel mass
- Remaining fuel mass
- Fuel consumption
- Fuel copying

This established fuel as an explicit simulation state.

---

### V6.2 — Fuel Effect on Lap Time

Fuel mass was added to the lap-time calculation.

The simplified calculation became:

    Lap time =
    base lap time
    + tire effect
    + fuel effect

This means a heavily fuelled car is slower than a lightly fuelled car.

---

### V6.3 — Shared Race Fuel

Fuel management was moved to the strategy level.

All stints within a strategy now consume the same fuel supply.

This prevents fuel from being incorrectly reset at pit stops.

---

### V6.4 — Dynamic Lap-Time Calculation

The `Stint` class received an explicit `lap_time_seconds()` method.

This separates:

1. Calculating the current lap time.
2. Updating tire age.
3. Updating fuel state.

This creates a cleaner foundation for future simulation features.

---

### V6.5 — Fuel-Aware Strategy Generation

Automatic strategy generation was extended to support fuel parameters.

Every generated strategy receives its own independent fuel object.

This ensures that evaluating one strategy does not affect another candidate strategy.

---

## 12. Current Project Architecture

After V6, the simulation package contains:

    src/
    └── f1_strategy/
        └── simulation/
            ├── fuel.py
            ├── generator.py
            ├── optimizer.py
            ├── pit_stop.py
            ├── race.py
            ├── stint.py
            ├── strategy.py
            ├── tire.py
            └── track.py

The major responsibilities are:

    Track
    └── Circuit characteristics

    Tire
    └── Tire compound and degradation

    Fuel
    └── Fuel state and consumption

    Stint
    └── Lap-by-lap tire and fuel simulation

    PitStop
    └── Pit-stop time

    RaceStrategy
    └── Complete sequence of stints and pit stops

    StrategyGenerator
    └── Creates candidate strategies

    StrategyOptimizer
    └── Finds the fastest candidate strategy

---

## 13. Current Simulation Flow

The complete V6 workflow is:

    Track
      ↓
    Strategy Generator
      ↓
    Candidate Strategies
      ↓
    Each strategy receives independent fuel
      ↓
    Strategy Optimizer
      ↓
    Race Strategy
      ↓
    Stint
      ↓
    Lap-by-lap simulation
      ↓
    Tire aging + fuel consumption
      ↓
    Total race time
      ↓
    Fastest strategy

---

## 14. Limitations of V6

The model is intentionally simplified.

Fuel consumption is currently constant:

    kg/lap = constant

The fuel penalty is also linear:

    fuel mass × constant

The simulation does not yet model:

- Weather
- Rain
- Track temperature
- Track evolution
- Traffic
- Safety cars
- Yellow flags
- Driver differences
- Engine modes
- ERS deployment
- DRS
- Qualifying performance
- Real F1 telemetry
- Historical race data

These limitations are intentional.

The goal of V6 is to establish a clean dynamic simulation foundation before introducing more complex variables.

---

## 15. Result

V6 transforms the project from a basic tire-and-strategy calculator into a more structured dynamic race simulator.

The simulation now considers two competing effects:

    Fuel burn
        ↓
    Car becomes lighter
        ↓
    Lap time decreases

    Tire degradation
        ↓
    Tire becomes slower
        ↓
    Lap time increases

These competing effects create a more meaningful race strategy problem.

The optimizer can now evaluate strategies in a simulation where the car's state changes continuously throughout the race.

---

## 16. Version Status

    V1.0  Basic race simulator                 ✓
    V2.0  Tire compounds and degradation       ✓
    V3.0  Pit stops and race strategies        ✓
    V4.0  Strategy optimization                ✓
    V5.0  Automatic strategy generation        ✓
    V6.0  Fuel and dynamic simulation          ✓

Test status:

    59 passed

V6 is complete.