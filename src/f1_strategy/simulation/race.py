from f1_strategy.simulation.tire import Tire
from f1_strategy.simulation.track import Track


class Race:

    def __init__(self, track: Track, tire: Tire):
        self.track = track
        self.tire = tire

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