from f1_strategy.simulation.track import Track


class Race:
    def __init__(self, track: Track):
        self.track = track

    def total_race_time_seconds(self) -> float:
        return self.track.lap_time_seconds() * self.track.number_of_laps