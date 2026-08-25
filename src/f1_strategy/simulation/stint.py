from f1_strategy.simulation.tire import Tire


class Stint:

    def __init__(self, tire: Tire, number_of_laps: int):
        if number_of_laps <= 0:
            raise ValueError("A stint must contain at least one lap")

        self.tire = tire
        self.number_of_laps = number_of_laps

    def total_time_seconds(self, base_lap_time: float) -> float:
        total_time = 0.0

        for _ in range(self.number_of_laps):
            lap_time = (
                base_lap_time
                + self.tire.performance_delta()
            )

            total_time += lap_time
            self.tire.age_one_lap()

        return total_time