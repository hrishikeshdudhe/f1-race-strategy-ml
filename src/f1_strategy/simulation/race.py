from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.strategy import RaceStrategy
from f1_strategy.simulation.track import Track


class Race:

    def __init__(
        self,
        track: Track,
        strategy: RaceStrategy,
        race_condition_schedule: RaceConditionSchedule | None = None,
    ):

        self.track = track
        self.strategy = strategy

        if self.strategy.total_laps() != self.track.number_of_laps:
            raise ValueError(
                "Strategy lap count must match race lap count"
            )

        if race_condition_schedule is None:
            race_condition_schedule = RaceConditionSchedule(
                self.track.number_of_laps
            )

        if (
            race_condition_schedule.number_of_laps
            != self.track.number_of_laps
        ):
            raise ValueError(
                "Race condition schedule lap count must match race lap count"
            )

        self.race_condition_schedule = race_condition_schedule

    def total_race_time_seconds(self) -> float:

        return self.strategy.total_time_seconds(
            self.track.lap_time_seconds(),
            self.race_condition_schedule,
        )