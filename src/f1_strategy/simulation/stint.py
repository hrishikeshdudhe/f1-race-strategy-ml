from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.tire import Tire


class Stint:

    def __init__(
        self,
        tire: Tire,
        number_of_laps: int,
        fuel: Fuel | None = None,
        fuel_time_penalty_per_kg: float = 0.03,
        race_condition: RaceCondition = RaceCondition.GREEN,
    ):

        if number_of_laps <= 0:
            raise ValueError(
                "Stint must contain at least one lap"
            )

        if fuel_time_penalty_per_kg < 0:
            raise ValueError(
                "Fuel time penalty cannot be negative"
            )

        self.tire = tire
        self.number_of_laps = number_of_laps
        self.fuel = fuel
        self.fuel_time_penalty_per_kg = (
            fuel_time_penalty_per_kg
        )
        self.race_condition = race_condition

    def lap_time_seconds(
        self,
        base_lap_time: float,
        race_condition: RaceCondition | None = None,
    ) -> float:

        condition = (
            race_condition
            if race_condition is not None
            else self.race_condition
        )

        fuel_penalty = 0.0

        if self.fuel is not None:
            fuel_penalty = (
                self.fuel.remaining_fuel_kg()
                * self.fuel_time_penalty_per_kg
            )

        normal_lap_time = (
            base_lap_time
            + self.tire.performance_delta()
            + fuel_penalty
        )

        return (
            normal_lap_time
            * condition.lap_time_multiplier
        )

    def simulate_lap(
        self,
        base_lap_time: float,
        race_condition: RaceCondition | None = None,
    ) -> float:

        lap_time = self.lap_time_seconds(
            base_lap_time,
            race_condition,
        )

        self.tire.age_one_lap()

        if self.fuel is not None:
            self.fuel.consume_one_lap()

        return lap_time

    def total_time_seconds(
        self,
        base_lap_time: float,
    ) -> float:

        total_time = 0.0

        for _ in range(self.number_of_laps):

            total_time += self.simulate_lap(
                base_lap_time
            )

        return total_time