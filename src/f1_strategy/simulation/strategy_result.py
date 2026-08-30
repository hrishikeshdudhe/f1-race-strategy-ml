from f1_strategy.simulation.race_condition import RaceCondition
from f1_strategy.simulation.race_condition_schedule import (
    RaceConditionSchedule,
)
from f1_strategy.simulation.strategy import RaceStrategy


class StrategyResult:

    def __init__(
        self,
        strategy: RaceStrategy,
        total_time_seconds: float,
        rank: int | None = None,
        time_delta_seconds: float = 0.0,
        time_gap_to_next_seconds: float = 0.0,
        race_condition_schedule: (
            RaceConditionSchedule | None
        ) = None,
        base_lap_time: float | None = None,
    ):
        self.strategy = strategy
        self.total_time_seconds = total_time_seconds
        self.rank = rank
        self.time_delta_seconds = time_delta_seconds
        self.time_gap_to_next_seconds = (
            time_gap_to_next_seconds
        )
        self.race_condition_schedule = (
            race_condition_schedule
        )
        self.base_lap_time = base_lap_time

    @property
    def pit_stop_time_seconds(self) -> float:
        return sum(
            pit_stop.time_seconds()
            for pit_stop in self.strategy.pit_stops
        )

    @property
    def number_of_pit_stops(self) -> int:
        return len(self.strategy.pit_stops)

    @property
    def total_laps(self) -> int:
        return self.strategy.total_laps()

    @property
    def tire_compounds(self) -> list[str]:
        return [
            stint.tire.compound.label
            for stint in self.strategy.stints
        ]

    @property
    def stint_laps(self) -> list[int]:
        return [
            stint.number_of_laps
            for stint in self.strategy.stints
        ]

    @property
    def number_of_stints(self) -> int:
        return len(self.strategy.stints)

    @property
    def average_lap_time_seconds(self) -> float:
        if self.total_laps == 0:
            return 0.0

        return (
            self.total_time_seconds
            / self.total_laps
        )

    @property
    def tire_strategy(self) -> str:
        return " -> ".join(
            compound.upper()
            for compound in self.tire_compounds
        )

    @property
    def time_gap_percentage(self) -> float:
        if self.time_delta_seconds <= 0.0:
            return 0.0

        fastest_time = (
            self.total_time_seconds
            - self.time_delta_seconds
        )

        if fastest_time <= 0.0:
            return 0.0

        return (
            self.time_delta_seconds
            / fastest_time
        ) * 100.0

    @property
    def green_laps(self) -> int:
        return self._count_condition(
            RaceCondition.GREEN
        )

    @property
    def yellow_laps(self) -> int:
        return self._count_condition(
            RaceCondition.YELLOW
        )

    @property
    def vsc_laps(self) -> int:
        return self._count_condition(
            RaceCondition.VSC
        )

    @property
    def safety_car_laps(self) -> int:
        return self._count_condition(
            RaceCondition.SAFETY_CAR
        )

    @property
    def race_condition_laps(self) -> int:
        return (
            self.yellow_laps
            + self.vsc_laps
            + self.safety_car_laps
        )

    @property
    def race_condition_delay_seconds(self) -> float:
        if (
            self.race_condition_schedule is None
            or self.base_lap_time is None
        ):
            return 0.0

        delay = 0.0

        for lap in range(
            1,
            self.total_laps + 1,
        ):
            condition = (
                self.race_condition_schedule.condition_for_lap(
                    lap
                )
            )

            delay += (
                self.base_lap_time
                * (
                    condition.lap_time_multiplier
                    - 1.0
                )
            )

        return delay

    @property
    def race_condition_summary(self) -> str:
        if self.race_condition_schedule is None:
            return "normal"

        conditions = []

        if self.yellow_laps > 0:
            conditions.append(
                f"yellow:{self.yellow_laps}"
            )

        if self.vsc_laps > 0:
            conditions.append(
                f"vsc:{self.vsc_laps}"
            )

        if self.safety_car_laps > 0:
            conditions.append(
                f"safety_car:{self.safety_car_laps}"
            )

        if not conditions:
            return "normal"

        return ";".join(conditions)

    def _count_condition(
        self,
        condition: RaceCondition,
    ) -> int:
        if self.race_condition_schedule is None:
            return 0

        count = 0

        for lap in range(
            1,
            self.total_laps + 1,
        ):
            if (
                self.race_condition_schedule.condition_for_lap(
                    lap
                )
                == condition
            ):
                count += 1

        return count

    def summary(self) -> str:
        rank_text = (
            str(self.rank)
            if self.rank is not None
            else "N/A"
        )

        tires = " -> ".join(
            compound.upper()
            for compound in self.tire_compounds
        )

        stint_laps = ", ".join(
            str(laps)
            for laps in self.stint_laps
        )

        return (
            f"Rank: {rank_text}\n"
            f"Total race time: "
            f"{self.total_time_seconds:.2f} s\n"
            f"Time difference: "
            f"+{self.time_delta_seconds:.2f} s\n"
            f"Time gap: "
            f"{self.time_gap_percentage:.3f}%\n"
            f"Gap to next: "
            f"{self.time_gap_to_next_seconds:.2f} s\n"
            f"Average lap time: "
            f"{self.average_lap_time_seconds:.2f} s\n"
            f"Stints: {self.number_of_stints}\n"
            f"Stint laps: {stint_laps}\n"
            f"Tires: {tires}\n"
            f"Pit stops: "
            f"{self.number_of_pit_stops}\n"
            f"Pit stop time: "
            f"{self.pit_stop_time_seconds:.2f} s\n"
            f"Race condition laps: "
            f"{self.race_condition_laps}\n"
            f"Race condition delay: "
            f"{self.race_condition_delay_seconds:.2f} s"
        )

    def __getitem__(self, index: int):
        if index == 0:
            return self.strategy

        if index == 1:
            return self.total_time_seconds

        raise IndexError(
            "StrategyResult index must be 0 or 1"
        )