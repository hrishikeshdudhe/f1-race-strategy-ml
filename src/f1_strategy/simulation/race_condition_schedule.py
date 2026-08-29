from f1_strategy.simulation.race_condition import RaceCondition


class RaceConditionSchedule:

    def __init__(
        self,
        number_of_laps: int,
        default_condition: RaceCondition = RaceCondition.GREEN,
    ):

        if number_of_laps <= 0:
            raise ValueError(
                "Number of laps must be positive"
            )

        self.number_of_laps = number_of_laps
        self.default_condition = default_condition
        self._conditions = {}

    def set_condition(
        self,
        start_lap: int,
        end_lap: int,
        condition: RaceCondition,
    ) -> None:

        if start_lap < 1:
            raise ValueError(
                "Start lap must be at least 1"
            )

        if end_lap < start_lap:
            raise ValueError(
                "End lap must not be before start lap"
            )

        if end_lap > self.number_of_laps:
            raise ValueError(
                "End lap cannot exceed race lap count"
            )

        for lap in range(start_lap, end_lap + 1):
            self._conditions[lap] = condition

    def condition_for_lap(self, lap_number: int) -> RaceCondition:

        if lap_number < 1 or lap_number > self.number_of_laps:
            raise ValueError(
                "Lap number must be within the race"
            )

        return self._conditions.get(
            lap_number,
            self.default_condition,
        )