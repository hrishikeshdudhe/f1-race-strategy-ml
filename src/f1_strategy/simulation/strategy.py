from f1_strategy.simulation.fuel import Fuel
from f1_strategy.simulation.pit_stop import PitStop
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

    def total_time_seconds(
        self,
        base_lap_time: float,
    ) -> float:

        total_time = 0.0

        for index, stint in enumerate(self.stints):

            if self.fuel is not None:
                stint.fuel = self.fuel

            total_time += (
                stint.total_time_seconds(base_lap_time)
            )

            if index < len(self.pit_stops):
                total_time += (
                    self.pit_stops[index].time_seconds()
                )

        return total_time