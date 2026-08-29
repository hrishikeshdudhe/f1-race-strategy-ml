from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.pit_stop import PitStop
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.stint import Stint


class RaceStrategy:

    def __init__(
        self,
        stints: list[Stint],
        pit_stops: list[PitStop],
        fuel: Fuel | None = None,
    ):

        if len(stints) != len(pit_stops) + 1:
            raise ValueError(
                "A strategy must have exactly one more stint than pit stop"
            )

        self.stints = stints
        self.pit_stops = pit_stops
        self.fuel = fuel

    def total_laps(self) -> int:
        return sum(
            stint.number_of_laps
            for stint in self.stints
        )

    def description(self) -> str:
        stint_descriptions = []

        for stint in self.stints:
            stint_descriptions.append(
                f"{stint.tire.compound.label.upper()} "
                f"({stint.number_of_laps} laps)"
            )

        return " → ".join(stint_descriptions)

    def total_time_seconds(
        self,
        base_lap_time: float,
        race_condition_schedule: RaceConditionSchedule | None = None,
    ) -> float:

        total_time = 0.0
        current_race_lap = 1

        for index, stint in enumerate(self.stints):

            if self.fuel is not None:
                stint.fuel = self.fuel

            for _ in range(stint.number_of_laps):

                race_condition = None

                if race_condition_schedule is not None:
                    race_condition = (
                        race_condition_schedule.condition_for_lap(
                            current_race_lap
                        )
                    )

                total_time += stint.simulate_lap(
                    base_lap_time,
                    race_condition,
                )

                current_race_lap += 1

            if index < len(self.pit_stops):
                total_time += (
                    self.pit_stops[index].time_seconds()
                )

        return total_time
