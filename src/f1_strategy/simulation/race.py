from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.track import Track


class Race:

    def __init__(
        self,
        track: Track,
        strategy: RaceStrategy,
    ):
        self.track = track
        self.strategy = strategy

        if self.strategy.total_laps() != self.track.number_of_laps:
            raise ValueError(
                "Strategy lap count must match race lap count"
            )

    def total_race_time_seconds(self) -> float:
        return self.strategy.total_time_seconds(
            self.track.lap_time_seconds()
        )